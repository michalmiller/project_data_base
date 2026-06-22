-- ============================================================
-- Function 2: calculate_store_revenue
-- Description: Calculates total revenue for a clothing store
--              across all its branches, applies bonus/penalty
--              logic, and logs the calculation to a summary table.
-- Elements used: Implicit Cursor (FOR..IN), Explicit Cursor,
--                DML (INSERT/UPDATE), Loops, Branching,
--                Exception Handling, Records
-- ============================================================

-- Create a table to log revenue calculations
CREATE TABLE IF NOT EXISTS store_revenue_log (
    log_id SERIAL PRIMARY KEY,
    store_id INT NOT NULL,
    store_name VARCHAR NOT NULL,
    total_revenue NUMERIC(12,2),
    branch_count INT,
    revenue_category VARCHAR(20),
    calculated_at TIMESTAMP DEFAULT NOW()
);

-- Drop if exists
DROP FUNCTION IF EXISTS calculate_store_revenue(INT);

CREATE OR REPLACE FUNCTION calculate_store_revenue(p_store_id INT)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    -- Record for store info
    v_store RECORD;
    
    -- Variables for calculations
    v_total_revenue NUMERIC(12,2) := 0;
    v_branch_revenue NUMERIC(12,2) := 0;
    v_branch_count INT := 0;
    v_sale_count INT := 0;
    v_revenue_category VARCHAR(20);
    v_bonus_multiplier NUMERIC(4,2) := 1.0;
    
    -- Explicit cursor for branches of the store
    cur_branches CURSOR FOR
        SELECT b.branch_id, b.branch_name, b.branch_status
        FROM branch b
        WHERE b.store_id = p_store_id;
    
    -- Record for cursor fetch
    v_branch RECORD;
    
    -- Variables for sale processing
    v_sale RECORD;
    
BEGIN
    -- Validate store exists
    SELECT store_id, store_name, city
    INTO v_store
    FROM clothingstore
    WHERE store_id = p_store_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Store with ID % does not exist', p_store_id;
    END IF;
    
    RAISE NOTICE '=== Calculating revenue for store: % (ID: %) ===',
                 v_store.store_name, p_store_id;
    
    -- Process each branch using explicit cursor
    OPEN cur_branches;
    LOOP
        FETCH cur_branches INTO v_branch;
        EXIT WHEN NOT FOUND;
        
        v_branch_count := v_branch_count + 1;
        v_branch_revenue := 0;
        v_sale_count := 0;
        
        -- Implicit cursor (FOR..IN) to iterate sales per branch
        FOR v_sale IN (
            SELECT s.sale_id, s.total_amount, s.sale_status
            FROM sale s
            WHERE s.branch_id = v_branch.branch_id
              AND s.sale_status IS NOT NULL
        )
        LOOP
            v_sale_count := v_sale_count + 1;
            
            -- Branching: apply different logic based on sale status
            IF v_sale.sale_status = 'completed' THEN
                v_branch_revenue := v_branch_revenue + COALESCE(v_sale.total_amount, 0);
            ELSIF v_sale.sale_status = 'returned' THEN
                v_branch_revenue := v_branch_revenue - COALESCE(v_sale.total_amount, 0) * 0.5;
            ELSIF v_sale.sale_status = 'pending' THEN
                v_branch_revenue := v_branch_revenue + COALESCE(v_sale.total_amount, 0) * 0.3;
            ELSE
                -- Unknown status - count partial
                v_branch_revenue := v_branch_revenue + COALESCE(v_sale.total_amount, 0) * 0.1;
            END IF;
        END LOOP;
        
        -- Apply bonus multiplier based on branch status
        IF v_branch.branch_status = 'active' THEN
            v_bonus_multiplier := 1.1;
        ELSIF v_branch.branch_status = 'new' THEN
            v_bonus_multiplier := 1.2;
        ELSIF v_branch.branch_status = 'closing' THEN
            v_bonus_multiplier := 0.8;
        ELSE
            v_bonus_multiplier := 1.0;
        END IF;
        
        v_branch_revenue := v_branch_revenue * v_bonus_multiplier;
        v_total_revenue := v_total_revenue + v_branch_revenue;
        
        RAISE NOTICE 'Branch: %, Sales: %, Revenue: %, Multiplier: %',
                     v_branch.branch_name, v_sale_count, 
                     v_branch_revenue, v_bonus_multiplier;
    END LOOP;
    CLOSE cur_branches;
    
    -- Determine revenue category with branching
    IF v_total_revenue > 100000 THEN
        v_revenue_category := 'PLATINUM';
    ELSIF v_total_revenue > 50000 THEN
        v_revenue_category := 'GOLD';
    ELSIF v_total_revenue > 20000 THEN
        v_revenue_category := 'SILVER';
    ELSIF v_total_revenue > 0 THEN
        v_revenue_category := 'BRONZE';
    ELSE
        v_revenue_category := 'NO REVENUE';
    END IF;
    
    -- DML: Log the calculation result
    INSERT INTO store_revenue_log (store_id, store_name, total_revenue, 
                                   branch_count, revenue_category)
    VALUES (p_store_id, v_store.store_name, v_total_revenue,
            v_branch_count, v_revenue_category);
    
    RAISE NOTICE '=== Total Revenue: % | Category: % | Branches: % ===',
                 v_total_revenue, v_revenue_category, v_branch_count;
    
    RETURN v_total_revenue;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE NOTICE 'ERROR: No data found for store ID %', p_store_id;
        RETURN -1;
    WHEN NUMERIC_VALUE_OUT_OF_RANGE THEN
        RAISE NOTICE 'ERROR: Numeric overflow during calculation for store %', p_store_id;
        RETURN -2;
    WHEN OTHERS THEN
        RAISE NOTICE 'ERROR: Unexpected error - %', SQLERRM;
        RETURN -99;
END;
$$;

-- ============================================================
-- Test the function
-- ============================================================
SELECT calculate_store_revenue(1);
SELECT calculate_store_revenue(5);
SELECT calculate_store_revenue(10);

-- View the log
SELECT * FROM store_revenue_log ORDER BY calculated_at DESC;
