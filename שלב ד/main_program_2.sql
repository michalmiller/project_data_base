-- ============================================================
-- Main Program 2: Store Revenue & Inventory Restock
-- Description: A comprehensive program that:
--   1. Calls calculate_store_revenue (Function 2) for stores
--   2. Calls manage_inventory_restock (Procedure 2) for branches
--   3. Generates a summary report comparing stores
-- Elements used: Function call, Procedure call, Cursor,
--                Loops, Branching, DML, Exception Handling
-- ============================================================

DO $$
DECLARE
    -- Cursor for stores that have branches
    cur_stores CURSOR FOR
        SELECT DISTINCT cs.store_id, cs.store_name, cs.city
        FROM clothingstore cs
        WHERE EXISTS (
            SELECT 1 FROM branch b WHERE b.store_id = cs.store_id
        )
        ORDER BY cs.store_id
        LIMIT 3;  -- Process top 3 stores
    
    -- Variables
    v_store RECORD;
    v_branch RECORD;
    v_revenue NUMERIC(12,2);
    v_total_revenue NUMERIC(12,2) := 0;
    v_stores_processed INT := 0;
    v_branches_restocked INT := 0;
    v_best_store_name VARCHAR := '';
    v_best_store_revenue NUMERIC(12,2) := 0;
    v_worst_store_name VARCHAR := '';
    v_worst_store_revenue NUMERIC(12,2) := 999999999;
    v_revenue_category VARCHAR;
    
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE '  MAIN PROGRAM 2: Store Revenue & Inventory Restock';
    RAISE NOTICE '  Execution Time: %', NOW();
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';
    
    -- =========================================
    -- PHASE 1: Calculate Revenue for Each Store
    -- =========================================
    RAISE NOTICE '************************************************************';
    RAISE NOTICE '  PHASE 1: Revenue Calculation';
    RAISE NOTICE '************************************************************';
    RAISE NOTICE '';
    
    OPEN cur_stores;
    LOOP
        FETCH cur_stores INTO v_store;
        EXIT WHEN NOT FOUND;
        
        v_stores_processed := v_stores_processed + 1;
        
        RAISE NOTICE '------------------------------------------------------------';
        RAISE NOTICE '  Store #%: % (City: %)',
                     v_stores_processed, v_store.store_name, v_store.city;
        RAISE NOTICE '------------------------------------------------------------';
        
        -- Call Function 2: calculate_store_revenue
        BEGIN
            v_revenue := calculate_store_revenue(v_store.store_id);
            
            RAISE NOTICE '  Revenue calculated: $%', v_revenue;
            
            -- Track totals
            v_total_revenue := v_total_revenue + v_revenue;
            
            -- Track best and worst
            IF v_revenue > v_best_store_revenue THEN
                v_best_store_revenue := v_revenue;
                v_best_store_name := v_store.store_name;
            END IF;
            
            IF v_revenue < v_worst_store_revenue THEN
                v_worst_store_revenue := v_revenue;
                v_worst_store_name := v_store.store_name;
            END IF;
            
            -- Categorize with branching
            IF v_revenue > 100000 THEN
                v_revenue_category := 'EXCELLENT';
            ELSIF v_revenue > 50000 THEN
                v_revenue_category := 'GOOD';
            ELSIF v_revenue > 10000 THEN
                v_revenue_category := 'AVERAGE';
            ELSIF v_revenue > 0 THEN
                v_revenue_category := 'LOW';
            ELSE
                v_revenue_category := 'NO REVENUE';
            END IF;
            
            RAISE NOTICE '  Category: %', v_revenue_category;
            
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE '  ERROR calculating revenue: %', SQLERRM;
                v_revenue := 0;
        END;
        
        RAISE NOTICE '';
    END LOOP;
    CLOSE cur_stores;
    
    -- =========================================
    -- PHASE 2: Restock Inventory for Branches
    -- =========================================
    RAISE NOTICE '************************************************************';
    RAISE NOTICE '  PHASE 2: Inventory Restock';
    RAISE NOTICE '************************************************************';
    RAISE NOTICE '';
    
    -- Process branches that belong to the stores we analyzed
    FOR v_branch IN (
        SELECT b.branch_id, b.branch_name, b.store_id, cs.store_name
        FROM branch b
        JOIN clothingstore cs ON b.store_id = cs.store_id
        WHERE b.store_id IN (
            SELECT DISTINCT cs2.store_id
            FROM clothingstore cs2
            WHERE EXISTS (SELECT 1 FROM branch b2 WHERE b2.store_id = cs2.store_id)
            ORDER BY cs2.store_id
            LIMIT 3
        )
        AND b.branch_status != 'closed'
        ORDER BY b.branch_id
        LIMIT 5  -- Limit to 5 branches for demo
    )
    LOOP
        RAISE NOTICE '------------------------------------------------------------';
        RAISE NOTICE '  Branch: % (Store: %)',
                     v_branch.branch_name, v_branch.store_name;
        RAISE NOTICE '------------------------------------------------------------';
        
        -- Call Procedure 2: manage_inventory_restock
        BEGIN
            CALL manage_inventory_restock(v_branch.branch_id, 1.5);
            v_branches_restocked := v_branches_restocked + 1;
            RAISE NOTICE '  Restock completed successfully.';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE '  WARNING: Restock failed - %', SQLERRM;
        END;
        
        RAISE NOTICE '';
    END LOOP;
    
    -- =========================================
    -- PHASE 3: Final Summary Report
    -- =========================================
    RAISE NOTICE '************************************************************';
    RAISE NOTICE '  PHASE 3: Summary Report';
    RAISE NOTICE '************************************************************';
    RAISE NOTICE '';
    RAISE NOTICE '  Stores Analyzed:       %', v_stores_processed;
    RAISE NOTICE '  Total Revenue:         $%', v_total_revenue;
    
    IF v_stores_processed > 0 THEN
        RAISE NOTICE '  Average Revenue:       $%', 
                     ROUND(v_total_revenue / v_stores_processed, 2);
    END IF;
    
    RAISE NOTICE '  Best Performing Store:  % ($%)', 
                 v_best_store_name, v_best_store_revenue;
    RAISE NOTICE '  Lowest Performing Store: % ($%)', 
                 v_worst_store_name, v_worst_store_revenue;
    RAISE NOTICE '  Branches Restocked:    %', v_branches_restocked;
    RAISE NOTICE '';
    
    -- Performance assessment with branching
    IF v_total_revenue > 200000 THEN
        RAISE NOTICE '  ASSESSMENT: Outstanding overall performance!';
    ELSIF v_total_revenue > 100000 THEN
        RAISE NOTICE '  ASSESSMENT: Good overall performance.';
    ELSIF v_total_revenue > 50000 THEN
        RAISE NOTICE '  ASSESSMENT: Average performance - room for improvement.';
    ELSE
        RAISE NOTICE '  ASSESSMENT: Below expectations - action required.';
    END IF;
    
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '  EXECUTION COMPLETE';
    RAISE NOTICE '  Check store_revenue_log and restock_log for details.';
    RAISE NOTICE '============================================================';

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '============================================================';
        RAISE NOTICE '  PROGRAM FATAL ERROR: %', SQLERRM;
        RAISE NOTICE '  SQLSTATE: %', SQLSTATE;
        RAISE NOTICE '============================================================';
END;
$$;

-- ============================================================
-- Verify results
-- ============================================================

-- View revenue log
SELECT * FROM store_revenue_log ORDER BY calculated_at DESC LIMIT 10;

-- View restock log
SELECT * FROM restock_log ORDER BY restocked_at DESC LIMIT 10;
