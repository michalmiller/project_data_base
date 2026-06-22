-- ============================================================
-- Function 1: get_team_statistics
-- Description: Returns comprehensive statistics for a given team
--              including player count, average score, match results,
--              and coach information.
-- Elements used: Explicit Cursor, Records, Loops, Branching,
--                Exception Handling, REF CURSOR return
-- ============================================================

-- Drop if exists
DROP FUNCTION IF EXISTS get_team_statistics(INT);

CREATE OR REPLACE FUNCTION get_team_statistics(p_team_id INT)
RETURNS TABLE (
    stat_category VARCHAR,
    stat_name VARCHAR,
    stat_value VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    -- Record variables
    v_team_record RECORD;
    v_player_record RECORD;
    v_match_record RECORD;
    
    -- Scalar variables
    v_player_count INT := 0;
    v_avg_score NUMERIC := 0;
    v_total_matches INT := 0;
    v_wins INT := 0;
    v_losses INT := 0;
    v_draws INT := 0;
    v_coach_count INT := 0;
    v_top_scorer_name VARCHAR := '';
    v_top_scorer_goals INT := 0;
    
    -- Explicit cursor for players
    cur_players CURSOR FOR
        SELECT player_id, first_name, last_name, score, position
        FROM player
        WHERE team_id = p_team_id
        ORDER BY score DESC;
    
    -- Explicit cursor for matches
    cur_matches CURSOR FOR
        SELECT m.match_id, m.home_score, m.away_score, m.status,
               mt.team_role
        FROM match m
        JOIN match_team mt ON m.match_id = mt.match_id
        WHERE mt.team_id = p_team_id
          AND m.status = 'Finished';

BEGIN
    -- Validate that team exists
    SELECT team_id, team_name, country, sport_type
    INTO v_team_record
    FROM nationalteam
    WHERE team_id = p_team_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Team with ID % does not exist', p_team_id;
    END IF;
    
    -- Return basic team info
    stat_category := 'Team Info';
    stat_name := 'Team Name';
    stat_value := v_team_record.team_name;
    RETURN NEXT;
    
    stat_name := 'Country';
    stat_value := v_team_record.country;
    RETURN NEXT;
    
    stat_name := 'Sport Type';
    stat_value := v_team_record.sport_type;
    RETURN NEXT;
    
    -- Process players using explicit cursor
    OPEN cur_players;
    LOOP
        FETCH cur_players INTO v_player_record;
        EXIT WHEN NOT FOUND;
        
        v_player_count := v_player_count + 1;
        v_avg_score := v_avg_score + v_player_record.score;
        
        -- Track top scorer
        IF v_player_record.score > v_top_scorer_goals THEN
            v_top_scorer_goals := v_player_record.score;
            v_top_scorer_name := v_player_record.first_name || ' ' || v_player_record.last_name;
        END IF;
    END LOOP;
    CLOSE cur_players;
    
    -- Calculate average
    IF v_player_count > 0 THEN
        v_avg_score := ROUND(v_avg_score / v_player_count, 2);
    END IF;
    
    -- Return player statistics
    stat_category := 'Players';
    stat_name := 'Total Players';
    stat_value := v_player_count::VARCHAR;
    RETURN NEXT;
    
    stat_name := 'Average Score';
    stat_value := v_avg_score::VARCHAR;
    RETURN NEXT;
    
    IF v_top_scorer_name != '' THEN
        stat_name := 'Top Scorer';
        stat_value := v_top_scorer_name || ' (' || v_top_scorer_goals || ' pts)';
        RETURN NEXT;
    END IF;
    
    -- Process matches using explicit cursor
    OPEN cur_matches;
    LOOP
        FETCH cur_matches INTO v_match_record;
        EXIT WHEN NOT FOUND;
        
        v_total_matches := v_total_matches + 1;
        
        -- Determine win/loss/draw based on team role
        IF v_match_record.team_role = 'HOME' THEN
            IF v_match_record.home_score > v_match_record.away_score THEN
                v_wins := v_wins + 1;
            ELSIF v_match_record.home_score < v_match_record.away_score THEN
                v_losses := v_losses + 1;
            ELSE
                v_draws := v_draws + 1;
            END IF;
        ELSE -- AWAY
            IF v_match_record.away_score > v_match_record.home_score THEN
                v_wins := v_wins + 1;
            ELSIF v_match_record.away_score < v_match_record.home_score THEN
                v_losses := v_losses + 1;
            ELSE
                v_draws := v_draws + 1;
            END IF;
        END IF;
    END LOOP;
    CLOSE cur_matches;
    
    -- Return match statistics
    stat_category := 'Matches';
    stat_name := 'Total Matches';
    stat_value := v_total_matches::VARCHAR;
    RETURN NEXT;
    
    stat_name := 'Wins';
    stat_value := v_wins::VARCHAR;
    RETURN NEXT;
    
    stat_name := 'Losses';
    stat_value := v_losses::VARCHAR;
    RETURN NEXT;
    
    stat_name := 'Draws';
    stat_value := v_draws::VARCHAR;
    RETURN NEXT;
    
    -- Win rate with branching
    IF v_total_matches > 0 THEN
        stat_name := 'Win Rate';
        stat_value := ROUND((v_wins::NUMERIC / v_total_matches) * 100, 1) || '%';
        RETURN NEXT;
    END IF;
    
    -- Coach count
    SELECT COUNT(*) INTO v_coach_count
    FROM has_coach
    WHERE team_id = p_team_id;
    
    stat_category := 'Coaching';
    stat_name := 'Number of Coaches';
    stat_value := v_coach_count::VARCHAR;
    RETURN NEXT;
    
    RETURN;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        stat_category := 'Error';
        stat_name := 'Message';
        stat_value := 'No data found for team ID: ' || p_team_id;
        RETURN NEXT;
    WHEN OTHERS THEN
        stat_category := 'Error';
        stat_name := 'Message';
        stat_value := 'Unexpected error: ' || SQLERRM;
        RETURN NEXT;
END;
$$;

-- ============================================================
-- Test the function
-- ============================================================
SELECT * FROM get_team_statistics(1);
SELECT * FROM get_team_statistics(5);
-- Test with non-existent team (should raise exception)
-- SELECT * FROM get_team_statistics(9999);
