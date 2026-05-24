-- =====================================================
-- Phase 2 - SQL Queries
-- Sports Tournament & Clothing Store Database
-- =====================================================


-- =====================================================
-- Query 1: Count players in each national team
-- Purpose: Shows how many players belong to each team
-- =====================================================

SELECT 
    nt.team_id,
    nt.team_name,
    COUNT(p.player_id) AS number_of_players
FROM national_team nt
LEFT JOIN player p
    ON nt.team_id = p.team_id
GROUP BY nt.team_id, nt.team_name
ORDER BY number_of_players DESC;


-- =====================================================
-- Query 2: Count matches in each tournament
-- Purpose: Shows how many matches are connected to each tournament
-- =====================================================

SELECT 
    t.tournament_id,
    t.tournament_name,
    COUNT(m.match_id) AS number_of_matches
FROM tournament t
LEFT JOIN match m
    ON t.tournament_id = m.tournament_id
GROUP BY t.tournament_id, t.tournament_name
ORDER BY number_of_matches DESC;


-- =====================================================
-- Query 3: Average attendance by match status
-- Purpose: Compares audience attendance between match statuses
-- =====================================================

SELECT
    status,
    AVG(attendance) AS average_attendance,
    MIN(attendance) AS minimum_attendance,
    MAX(attendance) AS maximum_attendance,
    COUNT(*) AS total_matches
FROM match
GROUP BY status
ORDER BY average_attendance DESC;


-- =====================================================
-- Query 4: Count match events by event type
-- Purpose: Shows which event types are most common
-- =====================================================

SELECT
    event_type,
    COUNT(*) AS total_events
FROM match_event
GROUP BY event_type
ORDER BY total_events DESC;


-- =====================================================
-- Query 5: Players with their team and store
-- Purpose: Displays each player with team and clothing store details
-- =====================================================

SELECT
    p.player_id,
    p.first_name,
    p.last_name,
    nt.team_name,
    cs.store_name
FROM player p
JOIN national_team nt
    ON p.team_id = nt.team_id
JOIN clothingstore cs
    ON p.store_id = cs.store_id
ORDER BY nt.team_name, p.last_name;


-- =====================================================
-- Query 6: Referees and number of matches they officiated
-- Purpose: Finds how many matches each referee managed
-- =====================================================

SELECT
    r.referee_id,
    r.first_name,
    r.last_name,
    COUNT(m.match_id) AS matches_officiated
FROM referee r
LEFT JOIN match m
    ON r.referee_id = m.referee_id
GROUP BY r.referee_id, r.first_name, r.last_name
ORDER BY matches_officiated DESC;


-- =====================================================
-- Query 7: Player with maximum goals/points without LIMIT
-- Purpose: Finds players with the highest points_or_goals value
-- =====================================================

SELECT
    p.player_id,
    p.first_name,
    p.last_name,
    ps.points_or_goals
FROM player p
JOIN player_statistics ps
    ON p.player_id = ps.player_id
WHERE ps.points_or_goals = (
    SELECT MAX(points_or_goals)
    FROM player_statistics
);


-- =====================================================
-- Query 8: Matches with more than 3 events
-- Purpose: Finds matches with high activity
-- =====================================================

SELECT
    m.match_id,
    m.match_date,
    COUNT(me.event_id) AS number_of_events
FROM match m
JOIN match_event me
    ON m.match_id = me.match_id
GROUP BY m.match_id, m.match_date
HAVING COUNT(me.event_id) > 3
ORDER BY number_of_events DESC;


-- =====================================================
-- Query 9: Tournaments organized by each clothing store
-- Purpose: Shows how many tournaments each store organizes
-- =====================================================

SELECT
    cs.store_id,
    cs.store_name,
    COUNT(t.tournament_id) AS tournaments_organized
FROM clothingstore cs
LEFT JOIN tournament t
    ON cs.store_id = t.store_id
GROUP BY cs.store_id, cs.store_name
ORDER BY tournaments_organized DESC;


-- =====================================================
-- Query 10: Teams participating in each match
-- Purpose: Uses the many-to-many table plays_in_match
-- =====================================================

SELECT
    m.match_id,
    m.match_date,
    nt.team_name
FROM match m
JOIN plays_in_match pim
    ON m.match_id = pim.match_id
JOIN national_team nt
    ON pim.team_id = nt.team_id
ORDER BY m.match_id;
-- =====================================================
-- Query 11: Add CHECK constraint for player height
-- Purpose: Prevents invalid player height values
-- =====================================================

ALTER TABLE player
ADD CONSTRAINT check_player_height
CHECK (height > 0);


-- =====================================================
-- Query 12: Add CHECK constraint for attendance
-- Purpose: Prevents negative attendance values
-- =====================================================

ALTER TABLE match
ADD CONSTRAINT check_match_attendance
CHECK (attendance >= 0);


-- =====================================================
-- Query 13: Update player position
-- Purpose: Demonstrates UPDATE command
-- Screenshot needed: before and after
-- =====================================================

SELECT * 
FROM player
WHERE player_id = 1000;

UPDATE player
SET position = 'Captain'
WHERE player_id = 1000;

SELECT * 
FROM player
WHERE player_id = 1000;


-- =====================================================
-- Query 14: Delete low severity events
-- Purpose: Demonstrates DELETE command
-- Screenshot needed: before and after
-- =====================================================

SELECT COUNT(*) AS low_events_before
FROM matchevent
WHERE severity_level = 'Low';

DELETE FROM matchevent
WHERE severity_level = 'Low';

SELECT COUNT(*) AS low_events_after
FROM matchevent
WHERE severity_level = 'Low';


-- =====================================================
-- Query 15: ROLLBACK example
-- Purpose: Demonstrates transaction rollback
-- =====================================================

BEGIN;

UPDATE match
SET attendance = attendance + 1000;

SELECT match_id, attendance
FROM match
ORDER BY match_id;

ROLLBACK;

SELECT match_id, attendance
FROM match
ORDER BY match_id;


-- =====================================================
-- Query 16: COMMIT example
-- Purpose: Demonstrates transaction commit
-- =====================================================

BEGIN;

UPDATE player
SET position = 'Substitute'
WHERE player_id = 1001;

COMMIT;

SELECT *
FROM player
WHERE player_id = 1001;
-- =====================================================
-- Query 17A: Count players per team using subquery
-- Purpose: Simple solution using subquery
-- =====================================================

EXPLAIN ANALYZE
SELECT
    nt.team_id,
    nt.team_name,
    (
        SELECT COUNT(*)
        FROM player p
        WHERE p.team_id = nt.team_id
    ) AS number_of_players
FROM nationalteam nt;


-- =====================================================
-- Query 17B: Count players per team using JOIN
-- Purpose: More efficient solution using JOIN and GROUP BY
-- =====================================================

EXPLAIN ANALYZE
SELECT
    nt.team_id,
    nt.team_name,
    COUNT(p.player_id) AS number_of_players
FROM nationalteam nt
LEFT JOIN player p
    ON nt.team_id = p.team_id
GROUP BY nt.team_id, nt.team_name;


-- =====================================================
-- Query 18A: Referee matches using subquery
-- Purpose: Counts matches per referee using subquery
-- =====================================================

EXPLAIN ANALYZE
SELECT
    r.referee_id,
    r.first_name,
    r.last_name,
    (
        SELECT COUNT(*)
        FROM match m
        WHERE m.referee_id = r.referee_id
    ) AS matches_count
FROM referee r;


-- =====================================================
-- Query 18B: Referee matches using JOIN
-- Purpose: Counts matches per referee using JOIN
-- =====================================================

EXPLAIN ANALYZE
SELECT
    r.referee_id,
    r.first_name,
    r.last_name,
    COUNT(m.match_id) AS matches_count
FROM referee r
LEFT JOIN match m
    ON r.referee_id = m.referee_id
GROUP BY r.referee_id, r.first_name, r.last_name;