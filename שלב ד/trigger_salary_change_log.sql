-- ============================================================
-- Trigger 2: trg_salary_change_log
-- Description: Fires AFTER UPDATE on the employee table when
--              the salary column changes. Logs the change,
--              enforces business rules (max raise percentage),
--              and updates branch budget tracking.
-- Trigger Type: AFTER UPDATE (on salary column)
-- Elements used: Branching, DML (INSERT, UPDATE), Exception,
--                Records, Calculations
-- ============================================================

-- Create salary change audit table
CREATE TABLE IF NOT EXISTS salary_change_log (
    log_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL,
    employee_name VARCHAR NOT NULL,
    branch_id INT,
    old_salary NUMERIC(10,2),
    new_salary NUMERIC(10,2),
    change_amount NUMERIC(10,2),
    change_percent NUMERIC(5,2),
    change_type VARCHAR(20),
    approved BOOLEAN DEFAULT TRUE,
    changed_by VARCHAR DEFAULT CURRENT_USER,
    changed_at TIMESTAMP DEFAULT NOW()
);

-- Create a budget summary table for branches
CREATE TABLE IF NOT EXISTS branch_salary_budget (
    branch_id INT PRIMARY KEY,
    total_salary_budget NUMERIC(12,2) DEFAULT 0,
    employee_count INT DEFAULT 0,
    avg_salary NUMERIC(10,2) DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Drop existing trigger and function
DROP TRIGGER IF EXISTS trg_salary_change_log ON employee;
DROP FUNCTION IF EXISTS fn_salary_change_log();

-- ============================================================
-- Trigger Function
-- ============================================================
CREATE OR REPLACE FUNCTION fn_salary_change_log()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_change_amount NUMERIC(10,2);
    v_change_percent NUMERIC(5,2);
    v_change_type VARCHAR(20);
    v_employee_name VARCHAR;
    v_branch_total NUMERIC(12,2);
    v_branch_emp_count INT;
    v_max_raise_percent NUMERIC := 50.0;  -- Business rule: max 50% raise
    
BEGIN
    -- Calculate change details
    v_change_amount := NEW.salary - OLD.salary;
    v_employee_name := NEW.first_name || ' ' || NEW.last_name;
    
    -- Calculate percentage (avoid division by zero)
    IF OLD.salary IS NOT NULL AND OLD.salary > 0 THEN
        v_change_percent := ROUND(((NEW.salary - OLD.salary) / OLD.salary) * 100, 2);
    ELSE
        v_change_percent := 100.00;
    END IF;
    
    -- Determine change type with branching
    IF v_change_amount > 0 THEN
        IF v_change_percent > 30 THEN
            v_change_type := 'MAJOR RAISE';
        ELSIF v_change_percent > 10 THEN
            v_change_type := 'RAISE';
        ELSE
            v_change_type := 'MINOR RAISE';
        END IF;
    ELSIF v_change_amount < 0 THEN
        IF ABS(v_change_percent) > 20 THEN
            v_change_type := 'MAJOR CUT';
        ELSE
            v_change_type := 'SALARY CUT';
        END IF;
    ELSE
        v_change_type := 'NO CHANGE';
        -- No actual change, skip logging
        RETURN NEW;
    END IF;
    
    -- Business rule: warn on excessive raises
    IF v_change_percent > v_max_raise_percent THEN
        RAISE NOTICE 'WARNING: Salary raise of %.2f%% for employee % (%) exceeds recommended maximum of %%. Change logged but flagged.',
                     v_change_percent, NEW.employee_id, v_employee_name, v_max_raise_percent;
    END IF;
    
    -- Business rule: negative salary check
    IF NEW.salary < 0 THEN
        RAISE EXCEPTION 'Invalid salary: cannot set negative salary (%.2f) for employee %',
                        NEW.salary, NEW.employee_id;
    END IF;
    
    -- DML: Log the salary change
    INSERT INTO salary_change_log (
        employee_id, employee_name, branch_id,
        old_salary, new_salary, change_amount,
        change_percent, change_type, approved
    )
    VALUES (
        NEW.employee_id, v_employee_name, NEW.branch_id,
        OLD.salary, NEW.salary, v_change_amount,
        v_change_percent, v_change_type,
        CASE WHEN v_change_percent > v_max_raise_percent THEN FALSE ELSE TRUE END
    );
    
    -- DML: Update branch salary budget summary
    IF NEW.branch_id IS NOT NULL THEN
        -- Calculate new branch totals
        SELECT COALESCE(SUM(salary), 0), COUNT(*)
        INTO v_branch_total, v_branch_emp_count
        FROM employee
        WHERE branch_id = NEW.branch_id;
        
        -- Adjust for the current change (trigger fires AFTER, so new value is in table)
        INSERT INTO branch_salary_budget (branch_id, total_salary_budget, 
                                          employee_count, avg_salary, last_updated)
        VALUES (NEW.branch_id, v_branch_total, v_branch_emp_count,
                CASE WHEN v_branch_emp_count > 0 
                     THEN ROUND(v_branch_total / v_branch_emp_count, 2)
                     ELSE 0 END,
                NOW())
        ON CONFLICT (branch_id) DO UPDATE
        SET total_salary_budget = EXCLUDED.total_salary_budget,
            employee_count = EXCLUDED.employee_count,
            avg_salary = EXCLUDED.avg_salary,
            last_updated = NOW();
    END IF;
    
    RAISE NOTICE 'Salary change logged: % (ID:%) | % -> % (% | %.2f%%)',
                 v_employee_name, NEW.employee_id,
                 OLD.salary, NEW.salary, v_change_type, v_change_percent;
    
    RETURN NEW;

EXCEPTION
    WHEN RAISE_EXCEPTION THEN
        RAISE;
    WHEN NUMERIC_VALUE_OUT_OF_RANGE THEN
        RAISE NOTICE 'ERROR: Numeric overflow in salary calculation for employee %',
                     NEW.employee_id;
        RAISE;
    WHEN OTHERS THEN
        RAISE NOTICE 'ERROR in salary trigger: % (SQLSTATE: %)', SQLERRM, SQLSTATE;
        RAISE;
END;
$$;

-- ============================================================
-- Create the Trigger (AFTER UPDATE)
-- ============================================================
CREATE TRIGGER trg_salary_change_log
    AFTER UPDATE OF salary ON employee
    FOR EACH ROW
    WHEN (OLD.salary IS DISTINCT FROM NEW.salary)
    EXECUTE FUNCTION fn_salary_change_log();

-- ============================================================
-- Test the trigger
-- ============================================================

-- View employee before update
SELECT employee_id, first_name, last_name, salary, branch_id
FROM employee
WHERE employee_id = 1;

-- Test 1: Normal raise (10%)
UPDATE employee
SET salary = salary * 1.10
WHERE employee_id = 1;

-- Test 2: Larger raise (25%)
UPDATE employee
SET salary = salary * 1.25
WHERE employee_id = 2;

-- Test 3: Salary cut
UPDATE employee
SET salary = salary * 0.85
WHERE employee_id = 3;

-- View the salary change log
SELECT * FROM salary_change_log ORDER BY changed_at DESC LIMIT 5;

-- View branch budget summary
SELECT * FROM branch_salary_budget ORDER BY branch_id LIMIT 5;
