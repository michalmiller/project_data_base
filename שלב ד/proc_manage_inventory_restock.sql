-- ============================================================
-- Procedure 2: manage_inventory_restock
-- Description: Checks all inventory items for a given branch,
--              identifies items below minimum stock level, and
--              restocks them. Applies different restock quantities
--              based on product category and current stock deficit.
-- Elements used: Explicit Cursor, Implicit Cursor (FOR..IN),
--                DML (UPDATE, INSERT), Loops, Branching,
--                Exception Handling, Records
-- ============================================================

-- Create a restock log table
CREATE TABLE IF NOT EXISTS restock_log (
    log_id SERIAL PRIMARY KEY,
    inventory_id INT NOT NULL,
    branch_id INT NOT NULL,
    product_name VARCHAR,
    old_quantity INT,
    restock_amount INT,
    new_quantity INT,
    restock_priority VARCHAR(20),
    restocked_at TIMESTAMP DEFAULT NOW()
);

-- Drop if exists
DROP PROCEDURE IF EXISTS manage_inventory_restock(INT, NUMERIC);

CREATE OR REPLACE PROCEDURE manage_inventory_restock(
    p_branch_id INT,
    p_restock_multiplier NUMERIC DEFAULT 1.5
)
LANGUAGE plpgsql
AS $$
DECLARE
    -- Explicit cursor for low-stock inventory items
    cur_low_stock CURSOR FOR
        SELECT i.inventory_id, i.quantity_in_stock, i.min_stock_level,
               i.color, i.size, i.shelf_location,
               i.product_id, i.branch_id
        FROM inventory i
        WHERE i.branch_id = p_branch_id
          AND i.quantity_in_stock < i.min_stock_level
        ORDER BY (i.min_stock_level - i.quantity_in_stock) DESC;
    
    -- Record variables
    v_item RECORD;
    v_branch RECORD;
    v_product RECORD;
    
    -- Calculation variables
    v_deficit INT := 0;
    v_restock_amount INT := 0;
    v_new_quantity INT := 0;
    v_restock_priority VARCHAR(20);
    v_items_restocked INT := 0;
    v_total_units_added INT := 0;
    v_category_name VARCHAR(50);
    v_product_name VARCHAR(100);
    
    -- Counter for WHILE loop
    v_max_iterations INT := 500;
    v_iteration INT := 0;
    
BEGIN
    -- Validate branch exists
    SELECT b.branch_id, b.branch_name, b.branch_status
    INTO v_branch
    FROM branch b
    WHERE b.branch_id = p_branch_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Branch with ID % does not exist', p_branch_id;
    END IF;
    
    -- Check if branch is active
    IF v_branch.branch_status = 'closed' THEN
        RAISE EXCEPTION 'Branch "%" is closed. Cannot restock a closed branch.', 
                        v_branch.branch_name;
    END IF;
    
    RAISE NOTICE '====================================================';
    RAISE NOTICE 'Inventory Restock for Branch: % (ID: %)',
                 v_branch.branch_name, p_branch_id;
    RAISE NOTICE 'Restock Multiplier: %', p_restock_multiplier;
    RAISE NOTICE '====================================================';
    
    -- Process low-stock items using explicit cursor
    OPEN cur_low_stock;
    LOOP
        FETCH cur_low_stock INTO v_item;
        EXIT WHEN NOT FOUND;
        
        -- Safety counter to prevent infinite loops
        v_iteration := v_iteration + 1;
        IF v_iteration > v_max_iterations THEN
            RAISE NOTICE 'WARNING: Reached maximum iteration limit (%).',
                         v_max_iterations;
            EXIT;
        END IF;
        
        -- Get product details
        v_product_name := 'Unknown Product';
        v_category_name := 'Unknown';
        
        BEGIN
            SELECT p.product_name, c.category_name
            INTO v_product_name, v_category_name
            FROM product p
            LEFT JOIN category c ON p.category_id = c.category_id
            WHERE p.product_id = v_item.product_id;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                v_product_name := 'Product #' || v_item.product_id;
                v_category_name := 'Uncategorized';
        END;
        
        -- Calculate deficit
        v_deficit := v_item.min_stock_level - v_item.quantity_in_stock;
        
        -- Branching: determine restock priority and amount based on deficit
        IF v_deficit >= 50 THEN
            v_restock_priority := 'CRITICAL';
            v_restock_amount := CEIL(v_deficit * p_restock_multiplier * 2);
        ELSIF v_deficit >= 20 THEN
            v_restock_priority := 'HIGH';
            v_restock_amount := CEIL(v_deficit * p_restock_multiplier * 1.5);
        ELSIF v_deficit >= 10 THEN
            v_restock_priority := 'MEDIUM';
            v_restock_amount := CEIL(v_deficit * p_restock_multiplier);
        ELSE
            v_restock_priority := 'LOW';
            v_restock_amount := v_deficit + 5;
        END IF;
        
        -- Additional branching based on category
        IF v_category_name IN ('Premium', 'Luxury', 'Designer') THEN
            -- Premium items get smaller restock (expensive)
            v_restock_amount := GREATEST(v_deficit, CEIL(v_restock_amount * 0.6));
        ELSIF v_category_name IN ('Basic', 'Essentials', 'Seasonal') THEN
            -- Basic items get larger restock (high demand)
            v_restock_amount := CEIL(v_restock_amount * 1.3);
        END IF;
        
        -- Calculate new quantity
        v_new_quantity := v_item.quantity_in_stock + v_restock_amount;
        
        -- DML: Update inventory quantity and restock date
        UPDATE inventory
        SET quantity_in_stock = v_new_quantity,
            last_restock_date = CURRENT_DATE
        WHERE inventory_id = v_item.inventory_id;
        
        -- DML: Log the restock action
        INSERT INTO restock_log (inventory_id, branch_id, product_name,
                                 old_quantity, restock_amount, new_quantity,
                                 restock_priority)
        VALUES (v_item.inventory_id, p_branch_id, v_product_name,
                v_item.quantity_in_stock, v_restock_amount, v_new_quantity,
                v_restock_priority);
        
        v_items_restocked := v_items_restocked + 1;
        v_total_units_added := v_total_units_added + v_restock_amount;
        
        RAISE NOTICE '[%] % | Deficit: % | Restocked: +% | New Qty: %',
                     v_restock_priority, v_product_name,
                     v_deficit, v_restock_amount, v_new_quantity;
    END LOOP;
    CLOSE cur_low_stock;
    
    -- Summary using implicit cursor to verify results
    RAISE NOTICE '====================================================';
    RAISE NOTICE 'Restock Summary:';
    RAISE NOTICE '  Items restocked: %', v_items_restocked;
    RAISE NOTICE '  Total units added: %', v_total_units_added;
    
    -- Implicit cursor: show remaining low stock items (if any)
    FOR v_item IN (
        SELECT COUNT(*) AS still_low
        FROM inventory
        WHERE branch_id = p_branch_id
          AND quantity_in_stock < min_stock_level
    )
    LOOP
        IF v_item.still_low > 0 THEN
            RAISE NOTICE '  WARNING: % items still below minimum stock!',
                         v_item.still_low;
        ELSE
            RAISE NOTICE '  All items are now at or above minimum stock level.';
        END IF;
    END LOOP;
    
    RAISE NOTICE '====================================================';
    
    -- Handle case where no items needed restocking
    IF v_items_restocked = 0 THEN
        RAISE NOTICE 'INFO: All inventory items for branch % are adequately stocked.',
                     p_branch_id;
    END IF;

EXCEPTION
    WHEN FOREIGN_KEY_VIOLATION THEN
        RAISE NOTICE 'ERROR: Foreign key violation during restock for branch %',
                     p_branch_id;
        RAISE;
    WHEN CHECK_VIOLATION THEN
        RAISE NOTICE 'ERROR: Check constraint violation - invalid quantity value';
        RAISE;
    WHEN OTHERS THEN
        RAISE NOTICE 'ERROR: Unexpected error during restock - % (SQLSTATE: %)',
                     SQLERRM, SQLSTATE;
        RAISE;
END;
$$;

-- ============================================================
-- Test the procedure
-- ============================================================
-- Check current low-stock items before
SELECT i.inventory_id, i.quantity_in_stock, i.min_stock_level,
       p.product_name, i.branch_id
FROM inventory i
JOIN product p ON i.product_id = p.product_id
WHERE i.branch_id = 1
  AND i.quantity_in_stock < i.min_stock_level
ORDER BY (i.min_stock_level - i.quantity_in_stock) DESC
LIMIT 10;

-- Execute the procedure
CALL manage_inventory_restock(1, 1.5);

-- Check results after
SELECT i.inventory_id, i.quantity_in_stock, i.min_stock_level,
       i.last_restock_date, p.product_name
FROM inventory i
JOIN product p ON i.product_id = p.product_id
WHERE i.branch_id = 1
ORDER BY i.inventory_id
LIMIT 10;

-- View the restock log
SELECT * FROM restock_log WHERE branch_id = 1 ORDER BY restocked_at DESC LIMIT 10;
