-- ============================================================
-- Procedure 1: update_player_scores
-- Description: Updates player scores based on match events (goals).
--              For each player in a given team, counts their goal
--              events and updates their score accordingly.
--              Also applies bonus points based on position.
-- Elements used: Explicit Cursor, DML (UPDATE), Loops,
--                Branching, Exception Handling, Records
-- ============================================================

-- Create a log table for score updates
CREATE TABLE IF NOT EXISTS player_score_log (
    log_id SERIAL PRIMARY KEY,
    player_id INT NOT NULL,
    player_name VARCHAR NOT NULL,
    old_score INT,
    new_score INT,
    bonus_applied INT,
    update_reason VARCHAR(100),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Drop if exists
DROP PROCEDURE IF EXISTS update_player_scores(INT, INT);

CREATE OR REPLACE PROCEDURE update_player_scores(
    p_team_id INT,
    p_bonus_points INT DEFAULT 5
)
LANGUAGE plpgsql
AS $$
DECLARE
    -- Explicit cursor for team players
    cur_players CURSOR FOR
        SELECT p.player_id, p.first_name, p.last_name, 
               p.score, p.position, p.team_id
        FROM player p
        WHERE p.team_id = p_team_id
        ORDER BY p.player_id;
    
    -- Record variables
    v_player RECORD;
    v_team RECORD;
    
    -- Calculation variables
    v_goal_count INT := 0;
    v_new_score INT := 0;
    v_position_bonus INT := 0;
    v_players_updated INT := 0;
    v_total_goals INT := 0;
    v_old_score INT := 0;
    
BEGIN
    -- Validate team exists
    SELECT team_id, team_name, sport_type
    INTO v_team
    FROM nationalteam
    WHERE team_id = p_team_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Team with ID % does not exist', p_team_id;
    END IF;
    
    RAISE NOTICE '====================================================';
    RAISE NOTICE 'Updating scores for team: % (ID: %)', v_team.team_name, p_team_id;
    RAISE NOTICE 'Bonus points per goal: %', p_bonus_points;
    RAISE NOTICE '====================================================';
    
    -- Process each player with explicit cursor
    OPEN cur_players;
    LOOP
        FETCH cur_players INTO v_player;
        EXIT WHEN NOT FOUND;
        
        v_old_score := v_player.score;
        v_goal_count := 0;
        v_position_bonus := 0;
        
        -- Count goal events for this player using implicit cursor
        -- (matchevent linked via match_team to player's team)
        SELECT COUNT(*)
        INTO v_goal_count
        FROM matchevent me
        JOIN match m ON me.match_id = m.match_id
        JOIN match_team mt ON m.match_id = mt.match_id
        WHERE mt.team_id = p_team_id
          AND me.event_type = 'Goal'
          AND me.event_minute BETWEEN 1 AND 90;
        
        -- Normalize: divide by team player count for per-player average
        IF v_goal_count > 0 THEN
            v_goal_count := GREATEST(1, v_goal_count / 
                GREATEST(1, (SELECT COUNT(*) FROM player WHERE team_id = p_team_id)));
        END IF;
        
        -- Branching: position-based bonus
        IF v_player.position = 'Forward' THEN
            v_position_bonus := p_bonus_points * 2;
        ELSIF v_player.position = 'Midfielder' THEN
            v_position_bonus := p_bonus_points;
        ELSIF v_player.position = 'Defender' THEN
            v_position_bonus := ROUND(p_bonus_points * 0.5);
        ELSIF v_player.position = 'Goalkeeper' THEN
            v_position_bonus := ROUND(p_bonus_points * 0.3);
        ELSE
            v_position_bonus := 1;
        END IF;
        
        -- Calculate new score
        v_new_score := v_old_score + (v_goal_count * p_bonus_points) + v_position_bonus;
        
        -- Cap score at 200
        IF v_new_score > 200 THEN
            v_new_score := 200;
        END IF;
        
        -- DML: Update the player's score
        UPDATE player
        SET score = v_new_score
        WHERE player_id = v_player.player_id;
        
        -- DML: Log the update
        INSERT INTO player_score_log (player_id, player_name, old_score, 
                                      new_score, bonus_applied, update_reason)
        VALUES (v_player.player_id, 
                v_player.first_name || ' ' || v_player.last_name,
                v_old_score, v_new_score, v_position_bonus,
                'Team score update - Position: ' || v_player.position);
        
        v_players_updated := v_players_updated + 1;
        v_total_goals := v_total_goals + v_goal_count;
        
        RAISE NOTICE 'Player: % % | Old: % | New: % | Position Bonus: %',
                     v_player.first_name, v_player.last_name,
                     v_old_score, v_new_score, v_position_bonus;
    END LOOP;
    CLOSE cur_players;
    
    RAISE NOTICE '====================================================';
    RAISE NOTICE 'Summary: % players updated, % total goal events processed',
                 v_players_updated, v_total_goals;
    RAISE NOTICE '====================================================';
    
    -- Final validation
    IF v_players_updated = 0 THEN
        RAISE NOTICE 'WARNING: No players found for team %', p_team_id;
    END IF;

EXCEPTION
    WHEN FOREIGN_KEY_VIOLATION THEN
        RAISE NOTICE 'ERROR: Foreign key violation while updating scores for team %', p_team_id;
        RAISE;
    WHEN NO_DATA_FOUND THEN
        RAISE NOTICE 'ERROR: Required data not found for team %', p_team_id;
        RAISE;
    WHEN OTHERS THEN
        RAISE NOTICE 'ERROR: Unexpected error - % (SQLSTATE: %)', SQLERRM, SQLSTATE;
        RAISE;
END;
$$;

-- ============================================================
-- Test the procedure
-- ============================================================
-- View scores before
SELECT player_id, first_name, last_name, score, position
FROM player WHERE team_id = 1 ORDER BY player_id LIMIT 10;

-- Execute the procedure
CALL update_player_scores(1, 5);

-- View scores after
SELECT player_id, first_name, last_name, score, position
FROM player WHERE team_id = 1 ORDER BY player_id LIMIT 10;

-- View the log
SELECT * FROM player_score_log ORDER BY updated_at DESC LIMIT 10;
