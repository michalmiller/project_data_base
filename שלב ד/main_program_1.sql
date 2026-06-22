-- ============================================================
-- Main Program 1: Team Analysis and Score Update
-- Description: A comprehensive program that:
--   1. Calls get_team_statistics (Function 1) to analyze a team
--   2. Calls update_player_scores (Procedure 1) to update scores
--   3. Compares before/after statistics
-- Elements used: Function call, Procedure call, Cursor,
--                Loops, Branching, DML, Exception Handling
-- ============================================================

DO $$
DECLARE
    -- Variables for team selection
    v_team_id INT;
    v_team_name VARCHAR;
    v_team_count INT;
    
    -- Variables for statistics comparison
    v_stat RECORD;
    v_before_avg_score NUMERIC := 0;
    v_after_avg_score NUMERIC := 0;
    v_before_total_players INT := 0;
    v_improvement NUMERIC := 0;
    
    -- Cursor to iterate over multiple teams
    cur_teams CURSOR FOR
        SELECT nt.team_id, nt.team_name
        FROM nationalteam nt
        WHERE EXISTS (
            SELECT 1 FROM player p WHERE p.team_id = nt.team_id
        )
        ORDER BY nt.team_id
        LIMIT 3;  -- Process top 3 teams with players
    
    v_team RECORD;
    v_teams_processed INT := 0;
    
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE '  MAIN PROGRAM 1: Team Analysis and Score Update';
    RAISE NOTICE '  Execution Time: %', NOW();
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';
    
    -- Count available teams
    SELECT COUNT(*) INTO v_team_count
    FROM nationalteam nt
    WHERE EXISTS (SELECT 1 FROM player p WHERE p.team_id = nt.team_id);
    
    RAISE NOTICE 'Found % teams with players in the database.', v_team_count;
    RAISE NOTICE '';
    
    -- Process each team using cursor
    OPEN cur_teams;
    LOOP
        FETCH cur_teams INTO v_team;
        EXIT WHEN NOT FOUND;
        
        v_teams_processed := v_teams_processed + 1;
        v_before_avg_score := 0;
        v_after_avg_score := 0;
        
        RAISE NOTICE '------------------------------------------------------------';
        RAISE NOTICE '  Processing Team #%: % (ID: %)', 
                     v_teams_processed, v_team.team_name, v_team.team_id;
        RAISE NOTICE '------------------------------------------------------------';
        
        -- =========================================
        -- STEP 1: Call Function - get_team_statistics
        -- =========================================
        RAISE NOTICE '';
        RAISE NOTICE '  [STEP 1] Calling get_team_statistics(%)...', v_team.team_id;
        RAISE NOTICE '  ----------------------------------------';
        
        FOR v_stat IN 
            SELECT * FROM get_team_statistics(v_team.team_id)
        LOOP
            RAISE NOTICE '    [%] % = %', 
                         v_stat.stat_category, v_stat.stat_name, v_stat.stat_value;
            
            -- Capture the average score before update
            IF v_stat.stat_name = 'Average Score' THEN
                BEGIN
                    v_before_avg_score := v_stat.stat_value::NUMERIC;
                EXCEPTION
                    WHEN OTHERS THEN
                        v_before_avg_score := 0;
                END;
            END IF;
            
            IF v_stat.stat_name = 'Total Players' THEN
                BEGIN
                    v_before_total_players := v_stat.stat_value::INT;
                EXCEPTION
                    WHEN OTHERS THEN
                        v_before_total_players := 0;
                END;
            END IF;
        END LOOP;
        
        RAISE NOTICE '';
        RAISE NOTICE '  Summary before update: Avg Score = %, Players = %',
                     v_before_avg_score, v_before_total_players;
        
        -- =========================================
        -- STEP 2: Call Procedure - update_player_scores
        -- =========================================
        RAISE NOTICE '';
        RAISE NOTICE '  [STEP 2] Calling update_player_scores(%, 5)...', v_team.team_id;
        RAISE NOTICE '  ----------------------------------------';
        
        CALL update_player_scores(v_team.team_id, 5);
        
        -- =========================================
        -- STEP 3: Call Function again to see changes
        -- =========================================
        RAISE NOTICE '';
        RAISE NOTICE '  [STEP 3] Re-analyzing team after score update...';
        RAISE NOTICE '  ----------------------------------------';
        
        FOR v_stat IN 
            SELECT * FROM get_team_statistics(v_team.team_id)
        LOOP
            -- Only show player stats for comparison
            IF v_stat.stat_category = 'Players' THEN
                RAISE NOTICE '    [%] % = %', 
                             v_stat.stat_category, v_stat.stat_name, v_stat.stat_value;
            END IF;
            
            -- Capture after average
            IF v_stat.stat_name = 'Average Score' THEN
                BEGIN
                    v_after_avg_score := v_stat.stat_value::NUMERIC;
                EXCEPTION
                    WHEN OTHERS THEN
                        v_after_avg_score := 0;
                END;
            END IF;
        END LOOP;
        
        -- =========================================
        -- STEP 4: Report improvement
        -- =========================================
        IF v_before_avg_score > 0 THEN
            v_improvement := ROUND(
                ((v_after_avg_score - v_before_avg_score) / v_before_avg_score) * 100, 2
            );
        ELSE
            v_improvement := 0;
        END IF;
        
        RAISE NOTICE '';
        RAISE NOTICE '  RESULT: Average score changed from % to % (%.2f%% change)',
                     v_before_avg_score, v_after_avg_score, v_improvement;
        
        -- Branching on improvement level
        IF v_improvement > 20 THEN
            RAISE NOTICE '  >> Significant improvement!';
        ELSIF v_improvement > 5 THEN
            RAISE NOTICE '  >> Moderate improvement.';
        ELSIF v_improvement > 0 THEN
            RAISE NOTICE '  >> Minor improvement.';
        ELSE
            RAISE NOTICE '  >> No improvement or scores already at max.';
        END IF;
        
        RAISE NOTICE '';
    END LOOP;
    CLOSE cur_teams;
    
    -- =========================================
    -- Final Summary
    -- =========================================
    RAISE NOTICE '============================================================';
    RAISE NOTICE '  EXECUTION COMPLETE';
    RAISE NOTICE '  Teams processed: %', v_teams_processed;
    RAISE NOTICE '  Check player_score_log for detailed update history.';
    RAISE NOTICE '============================================================';

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '============================================================';
        RAISE NOTICE '  PROGRAM ERROR: %', SQLERRM;
        RAISE NOTICE '  SQLSTATE: %', SQLSTATE;
        RAISE NOTICE '============================================================';
END;
$$;

-- ============================================================
-- Verify results
-- ============================================================

-- View recent score updates
SELECT * FROM player_score_log ORDER BY updated_at DESC LIMIT 15;

-- View team stats for verification
SELECT * FROM get_team_statistics(1);
