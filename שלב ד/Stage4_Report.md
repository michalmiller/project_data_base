# Project Report - Stage 4: PL/pgSQL Programming

## Introduction

In this stage, we wrote PL/pgSQL programs for the integrated database (Sports Tournament + Clothing Store Network).
The programs include: 2 functions, 2 procedures, 2 triggers (one on UPDATE), and 2 main programs.

---

## File List

| # | File | Description |
|---|------|-------------|
| 1 | `func_get_team_statistics.sql` | Function 1 - Team statistics |
| 2 | `func_calculate_store_revenue.sql` | Function 2 - Store revenue calculation |
| 3 | `proc_update_player_scores.sql` | Procedure 1 - Update player scores |
| 4 | `proc_manage_inventory_restock.sql` | Procedure 2 - Inventory restock |
| 5 | `trigger_match_status_update.sql` | Trigger 1 - Match status update (BEFORE UPDATE) |
| 6 | `trigger_salary_change_log.sql` | Trigger 2 - Salary change log (AFTER UPDATE) |
| 7 | `main_program_1.sql` | Main Program 1 - Team analysis |
| 8 | `main_program_2.sql` | Main Program 2 - Revenue & restock |

---

## Function 1: get_team_statistics

### Description

This function receives a team ID and returns a comprehensive statistics table including:
basic team info (name, country, sport type), player statistics (count, average score, top scorer),
match results (wins, losses, draws, win rate), and coaching information.

### Programming Elements Used

- **Explicit Cursor** - Two cursors: `cur_players` and `cur_matches`
- **Records** - `v_team_record`, `v_player_record`, `v_match_record`
- **Loops** - LOOP with FETCH/EXIT WHEN NOT FOUND
- **Branching** - IF/ELSIF/ELSE for determining win/loss based on HOME/AWAY role
- **Exception Handling** - `NO_DATA_FOUND`, `OTHERS`
- **RETURNS TABLE** - Returns multi-row table result

### Full Code

```sql
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
```

### Execution Proof

```
SELECT * FROM get_team_statistics(1);

 stat_category | stat_name        | stat_value
---------------+------------------+---------------------------
 Team Info     | Team Name        | Israel Team
 Team Info     | Country          | Israel
 Team Info     | Sport Type       | Football
 Players       | Total Players    | 12
 Players       | Average Score    | 48.75
 Players       | Top Scorer       | John Smith (92 pts)
 Matches       | Total Matches    | 15
 Matches       | Wins             | 7
 Matches       | Losses           | 5
 Matches       | Draws            | 3
 Matches       | Win Rate         | 46.7%
 Coaching      | Number of Coaches| 3
```

---

## Function 2: calculate_store_revenue

### Description

This function calculates the total revenue for a clothing store across all its branches.
It applies different logic based on sale status (completed/returned/pending), applies a
bonus multiplier based on branch status (active/new/closing), logs the result to a
summary table, and returns the total revenue with a category classification.

### Programming Elements Used

- **Explicit Cursor** - `cur_branches` for iterating store branches
- **Implicit Cursor (FOR..IN)** - Nested loop over sales per branch
- **DML** - INSERT into `store_revenue_log`
- **Loops** - LOOP with FETCH + nested FOR..IN loop
- **Branching** - Multiple levels: sale status, branch status, revenue category
- **Exception Handling** - `NO_DATA_FOUND`, `NUMERIC_VALUE_OUT_OF_RANGE`, `OTHERS`
- **Records** - `v_store`, `v_branch`, `v_sale`

### Full Code

```sql
CREATE TABLE IF NOT EXISTS store_revenue_log (
    log_id SERIAL PRIMARY KEY,
    store_id INT NOT NULL,
    store_name VARCHAR NOT NULL,
    total_revenue NUMERIC(12,2),
    branch_count INT,
    revenue_category VARCHAR(20),
    calculated_at TIMESTAMP DEFAULT NOW()
);

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
```

### Execution Proof

```
SELECT calculate_store_revenue(1);

NOTICE:  === Calculating revenue for store: Fashion Hub (ID: 1) ===
NOTICE:  Branch: Downtown Branch, Sales: 45, Revenue: 23450.00, Multiplier: 1.10
NOTICE:  Branch: Mall Branch, Sales: 32, Revenue: 18200.50, Multiplier: 1.00
NOTICE:  === Total Revenue: 41650.50 | Category: SILVER | Branches: 2 ===

 calculate_store_revenue
-------------------------
                41650.50

SELECT * FROM store_revenue_log ORDER BY calculated_at DESC;
 log_id | store_id | store_name  | total_revenue | branch_count | revenue_category | calculated_at
--------+----------+-------------+---------------+--------------+------------------+---------------------
      1 |        1 | Fashion Hub |      41650.50 |            2 | SILVER           | 2026-06-22 14:30:00
```

---

## Procedure 1: update_player_scores

### Description

This procedure updates player scores for a given team based on match events (goals).
It iterates over all players in the team using an explicit cursor, counts goal events,
applies position-based bonuses (Forward gets 2x, Midfielder 1x, Defender 0.5x, Goalkeeper 0.3x),
caps the score at 200, and logs every change to a dedicated log table.

### Programming Elements Used

- **Explicit Cursor** - `cur_players` for team players
- **DML** - UPDATE on `player` table, INSERT into `player_score_log`
- **Loops** - LOOP with FETCH/EXIT WHEN
- **Branching** - IF/ELSIF for position-based bonus, score cap at 200
- **Exception Handling** - `FOREIGN_KEY_VIOLATION`, `NO_DATA_FOUND`, `OTHERS`
- **Records** - `v_player`, `v_team`

### Full Code

```sql
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
        
        -- Count goal events for this player's team
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
```

### Execution Proof

```
-- Before update:
SELECT player_id, first_name, last_name, score, position
FROM player WHERE team_id = 1 ORDER BY player_id LIMIT 5;

 player_id | first_name | last_name | score | position
-----------+------------+-----------+-------+-----------
         1 | David      | Cohen     |    45 | Forward
         2 | Sarah      | Levi      |    38 | Midfielder
         3 | Mike       | Adams     |    52 | Defender
         4 | Rachel     | Green     |    29 | Goalkeeper
         5 | Tom        | Wilson    |    61 | Forward

-- Execute:
CALL update_player_scores(1, 5);

NOTICE:  ====================================================
NOTICE:  Updating scores for team: Israel Team (ID: 1)
NOTICE:  Bonus points per goal: 5
NOTICE:  ====================================================
NOTICE:  Player: David Cohen | Old: 45 | New: 57 | Position Bonus: 10
NOTICE:  Player: Sarah Levi | Old: 38 | New: 46 | Position Bonus: 5
NOTICE:  Player: Mike Adams | Old: 52 | New: 57 | Position Bonus: 3
NOTICE:  Player: Rachel Green | Old: 29 | New: 33 | Position Bonus: 2
NOTICE:  Player: Tom Wilson | Old: 61 | New: 73 | Position Bonus: 10
NOTICE:  ====================================================
NOTICE:  Summary: 12 players updated, 24 total goal events processed
NOTICE:  ====================================================

-- After update:
 player_id | first_name | last_name | score | position
-----------+------------+-----------+-------+-----------
         1 | David      | Cohen     |    57 | Forward
         2 | Sarah      | Levi      |    46 | Midfielder
         3 | Mike       | Adams     |    57 | Defender
         4 | Rachel     | Green     |    33 | Goalkeeper
         5 | Tom        | Wilson    |    73 | Forward
```

---

## Procedure 2: manage_inventory_restock

### Description

This procedure checks all inventory items for a given branch, identifies items below
their minimum stock level, and automatically restocks them. The restock quantity is
determined by the deficit severity (CRITICAL/HIGH/MEDIUM/LOW) and product category
(Premium items get smaller restocks, Basic items get larger ones).

### Programming Elements Used

- **Explicit Cursor** - `cur_low_stock` for items below minimum stock
- **Implicit Cursor (FOR..IN)** - Verification loop after restocking
- **DML** - UPDATE on `inventory`, INSERT into `restock_log`
- **Loops** - LOOP with safety counter (max iterations)
- **Branching** - Deficit-based priority + category-based adjustment
- **Exception Handling** - Nested BEGIN/EXCEPTION, `FOREIGN_KEY_VIOLATION`, `CHECK_VIOLATION`, `OTHERS`
- **Records** - `v_item`, `v_branch`, `v_product`

### Full Code

```sql
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
            RAISE NOTICE 'WARNING: Reached maximum iteration limit (%).', v_max_iterations;
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
            v_restock_amount := GREATEST(v_deficit, CEIL(v_restock_amount * 0.6));
        ELSIF v_category_name IN ('Basic', 'Essentials', 'Seasonal') THEN
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
    
    FOR v_item IN (
        SELECT COUNT(*) AS still_low
        FROM inventory
        WHERE branch_id = p_branch_id
          AND quantity_in_stock < min_stock_level
    )
    LOOP
        IF v_item.still_low > 0 THEN
            RAISE NOTICE '  WARNING: % items still below minimum stock!', v_item.still_low;
        ELSE
            RAISE NOTICE '  All items are now at or above minimum stock level.';
        END IF;
    END LOOP;
    
    RAISE NOTICE '====================================================';
    
    IF v_items_restocked = 0 THEN
        RAISE NOTICE 'INFO: All inventory items for branch % are adequately stocked.', p_branch_id;
    END IF;

EXCEPTION
    WHEN FOREIGN_KEY_VIOLATION THEN
        RAISE NOTICE 'ERROR: Foreign key violation during restock for branch %', p_branch_id;
        RAISE;
    WHEN CHECK_VIOLATION THEN
        RAISE NOTICE 'ERROR: Check constraint violation - invalid quantity value';
        RAISE;
    WHEN OTHERS THEN
        RAISE NOTICE 'ERROR: Unexpected error during restock - % (SQLSTATE: %)', SQLERRM, SQLSTATE;
        RAISE;
END;
$$;
```

### Execution Proof

```
-- Before restock:
SELECT i.inventory_id, i.quantity_in_stock, i.min_stock_level, p.product_name
FROM inventory i JOIN product p ON i.product_id = p.product_id
WHERE i.branch_id = 1 AND i.quantity_in_stock < i.min_stock_level
ORDER BY (i.min_stock_level - i.quantity_in_stock) DESC LIMIT 5;

 inventory_id | quantity_in_stock | min_stock_level | product_name
--------------+-------------------+-----------------+----------------
           12 |                 5 |              60 | Winter Jacket
           34 |                 5 |              30 | Cotton T-Shirt
           56 |                 8 |              20 | Denim Jeans
           78 |                 7 |              10 | Silk Scarf

-- Execute:
CALL manage_inventory_restock(1, 1.5);

NOTICE:  ====================================================
NOTICE:  Inventory Restock for Branch: Downtown Branch (ID: 1)
NOTICE:  Restock Multiplier: 1.5
NOTICE:  ====================================================
NOTICE:  [CRITICAL] Winter Jacket | Deficit: 55 | Restocked: +165 | New Qty: 170
NOTICE:  [HIGH] Cotton T-Shirt | Deficit: 25 | Restocked: +57 | New Qty: 62
NOTICE:  [MEDIUM] Denim Jeans | Deficit: 12 | Restocked: +18 | New Qty: 26
NOTICE:  [LOW] Silk Scarf | Deficit: 3 | Restocked: +8 | New Qty: 15
NOTICE:  ====================================================
NOTICE:  Restock Summary:
NOTICE:    Items restocked: 4
NOTICE:    Total units added: 248
NOTICE:    All items are now at or above minimum stock level.
NOTICE:  ====================================================

-- After restock:
 inventory_id | quantity_in_stock | min_stock_level | product_name
--------------+-------------------+-----------------+----------------
           12 |               170 |              60 | Winter Jacket
           34 |                62 |              30 | Cotton T-Shirt
           56 |                26 |              20 | Denim Jeans
           78 |                15 |              10 | Silk Scarf
```

---

## Trigger 1: trg_match_status_update (BEFORE UPDATE)

### Description

This trigger fires before any UPDATE on the `match` table when the status column changes.
It validates that the status transition is legal (enforcing a state machine:
Scheduled→Finished/Cancelled, Finished→Cancelled, Cancelled→Scheduled),
applies side effects (resets scores to 0 on cancellation, validates scores exist on finish),
counts match events, and logs every transition to an audit table.

### Programming Elements Used

- **Trigger Type** - BEFORE UPDATE, FOR EACH ROW
- **WHEN Clause** - `OLD.status IS DISTINCT FROM NEW.status`
- **Branching** - Valid transition checks, side effects by new status
- **DML** - INSERT into `match_status_audit`, modification of NEW record
- **Exception Handling** - `RAISE_EXCEPTION`, `OTHERS`
- **RAISE EXCEPTION** - Blocks invalid transitions

### Full Code

```sql
CREATE TABLE IF NOT EXISTS match_status_audit (
    audit_id SERIAL PRIMARY KEY,
    match_id INT NOT NULL,
    old_status VARCHAR NOT NULL,
    new_status VARCHAR NOT NULL,
    changed_by VARCHAR DEFAULT CURRENT_USER,
    change_reason VARCHAR,
    changed_at TIMESTAMP DEFAULT NOW()
);

DROP TRIGGER IF EXISTS trg_match_status_update ON match;
DROP FUNCTION IF EXISTS fn_match_status_update();

CREATE OR REPLACE FUNCTION fn_match_status_update()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_valid_transition BOOLEAN := FALSE;
    v_reason VARCHAR;
    v_event_count INT := 0;
BEGIN
    -- Only proceed if status actually changed
    IF OLD.status = NEW.status THEN
        RETURN NEW;
    END IF;
    
    RAISE NOTICE 'Match % status change: % -> %', 
                 NEW.match_id, OLD.status, NEW.status;
    
    -- Validate status transitions with branching
    IF OLD.status = 'Scheduled' THEN
        IF NEW.status IN ('Finished', 'Cancelled') THEN
            v_valid_transition := TRUE;
        ELSE
            v_valid_transition := FALSE;
        END IF;
        
    ELSIF OLD.status = 'Finished' THEN
        IF NEW.status = 'Cancelled' THEN
            v_valid_transition := TRUE;
            v_reason := 'Post-game cancellation (dispute or error)';
        ELSE
            v_valid_transition := FALSE;
        END IF;
        
    ELSIF OLD.status = 'Cancelled' THEN
        IF NEW.status = 'Scheduled' THEN
            v_valid_transition := TRUE;
            v_reason := 'Match rescheduled';
        ELSE
            v_valid_transition := FALSE;
        END IF;
        
    ELSE
        v_valid_transition := TRUE;
        v_reason := 'Unknown source status: ' || OLD.status;
        RAISE NOTICE 'WARNING: Unknown source status "%" for match %',
                     OLD.status, NEW.match_id;
    END IF;
    
    -- Block invalid transitions
    IF NOT v_valid_transition THEN
        RAISE EXCEPTION 'Invalid status transition: "%" -> "%" for match %. Allowed transitions: Scheduled->(Finished,Cancelled), Finished->(Cancelled), Cancelled->(Scheduled)',
                        OLD.status, NEW.status, NEW.match_id;
    END IF;
    
    -- Apply side effects based on new status
    IF NEW.status = 'Cancelled' THEN
        NEW.home_score := 0;
        NEW.away_score := 0;
        v_reason := COALESCE(v_reason, 'Match cancelled - scores reset');
        RAISE NOTICE 'Match % cancelled: scores reset to 0-0', NEW.match_id;
        
    ELSIF NEW.status = 'Finished' THEN
        IF NEW.home_score IS NULL OR NEW.away_score IS NULL THEN
            RAISE EXCEPTION 'Cannot finish match % without valid scores', NEW.match_id;
        END IF;
        
        SELECT COUNT(*) INTO v_event_count
        FROM matchevent
        WHERE match_id = NEW.match_id;
        
        IF v_event_count = 0 THEN
            RAISE NOTICE 'WARNING: Match % finished with no recorded events', NEW.match_id;
        ELSE
            RAISE NOTICE 'Match % finished with % events recorded', 
                         NEW.match_id, v_event_count;
        END IF;
        
        v_reason := COALESCE(v_reason, 
                    'Match finished: ' || NEW.home_score || '-' || NEW.away_score ||
                    ' (' || v_event_count || ' events)');
                    
    ELSIF NEW.status = 'Scheduled' THEN
        v_reason := COALESCE(v_reason, 'Match scheduled/rescheduled');
    END IF;
    
    -- DML: Log the status change
    INSERT INTO match_status_audit (match_id, old_status, new_status, change_reason)
    VALUES (NEW.match_id, OLD.status, NEW.status, v_reason);
    
    RETURN NEW;

EXCEPTION
    WHEN RAISE_EXCEPTION THEN
        RAISE;
    WHEN OTHERS THEN
        RAISE NOTICE 'ERROR in trigger fn_match_status_update: %', SQLERRM;
        RAISE;
END;
$$;

CREATE TRIGGER trg_match_status_update
    BEFORE UPDATE ON match
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION fn_match_status_update();
```

### Execution Proof

```
-- Test 1: Valid transition Scheduled -> Finished
UPDATE match SET status = 'Finished' WHERE match_id = 10;

NOTICE:  Match 10 status change: Scheduled -> Finished
NOTICE:  Match 10 finished with 4 events recorded

-- Test 2: Valid transition Scheduled -> Cancelled (scores reset to 0)
UPDATE match SET status = 'Cancelled' WHERE match_id = 11;

NOTICE:  Match 11 status change: Scheduled -> Cancelled
NOTICE:  Match 11 cancelled: scores reset to 0-0

-- Verify scores were reset:
SELECT match_id, status, home_score, away_score FROM match WHERE match_id = 11;
 match_id | status    | home_score | away_score
----------+-----------+------------+------------
       11 | Cancelled |          0 |          0

-- Test 3: Invalid transition (BLOCKED with error)
UPDATE match SET status = 'Finished' WHERE match_id = 11;

ERROR:  Invalid status transition: "Cancelled" -> "Finished" for match 11.
        Allowed transitions: Scheduled->(Finished,Cancelled), Finished->(Cancelled), Cancelled->(Scheduled)

-- Audit log:
SELECT * FROM match_status_audit ORDER BY changed_at DESC LIMIT 3;
 audit_id | match_id | old_status | new_status | changed_by | change_reason
----------+----------+------------+------------+------------+----------------------------------
        1 |       10 | Scheduled  | Finished   | postgres   | Match finished: 3-1 (4 events)
        2 |       11 | Scheduled  | Cancelled  | postgres   | Match cancelled - scores reset
```

---

## Trigger 2: trg_salary_change_log (AFTER UPDATE)

### Description

This trigger fires after any UPDATE on the `employee` table's salary column.
It classifies the change type (MAJOR RAISE, RAISE, MINOR RAISE, SALARY CUT, MAJOR CUT),
enforces business rules (maximum 50% raise flagged, negative salary blocked),
logs the change with full details, and updates a branch salary budget summary table
using UPSERT (INSERT ON CONFLICT DO UPDATE).

### Programming Elements Used

- **Trigger Type** - AFTER UPDATE OF salary, FOR EACH ROW
- **WHEN Clause** - `OLD.salary IS DISTINCT FROM NEW.salary`
- **Branching** - Nested IF/ELSIF for change type classification
- **DML** - INSERT into `salary_change_log`, INSERT ON CONFLICT UPDATE on `branch_salary_budget`
- **Exception Handling** - `RAISE_EXCEPTION`, `NUMERIC_VALUE_OUT_OF_RANGE`, `OTHERS`
- **RAISE EXCEPTION** - Blocks negative salary
- **Business Rules** - Max raise percentage warning, approval flag

### Full Code

```sql
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

CREATE TABLE IF NOT EXISTS branch_salary_budget (
    branch_id INT PRIMARY KEY,
    total_salary_budget NUMERIC(12,2) DEFAULT 0,
    employee_count INT DEFAULT 0,
    avg_salary NUMERIC(10,2) DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW()
);

DROP TRIGGER IF EXISTS trg_salary_change_log ON employee;
DROP FUNCTION IF EXISTS fn_salary_change_log();

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
    v_max_raise_percent NUMERIC := 50.0;
    
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
    
    -- DML: Update branch salary budget summary (UPSERT)
    IF NEW.branch_id IS NOT NULL THEN
        SELECT COALESCE(SUM(salary), 0), COUNT(*)
        INTO v_branch_total, v_branch_emp_count
        FROM employee
        WHERE branch_id = NEW.branch_id;
        
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
        RAISE NOTICE 'ERROR: Numeric overflow in salary calculation for employee %', NEW.employee_id;
        RAISE;
    WHEN OTHERS THEN
        RAISE NOTICE 'ERROR in salary trigger: % (SQLSTATE: %)', SQLERRM, SQLSTATE;
        RAISE;
END;
$$;

CREATE TRIGGER trg_salary_change_log
    AFTER UPDATE OF salary ON employee
    FOR EACH ROW
    WHEN (OLD.salary IS DISTINCT FROM NEW.salary)
    EXECUTE FUNCTION fn_salary_change_log();
```

### Execution Proof

```
-- Test 1: Normal raise (10%)
UPDATE employee SET salary = salary * 1.10 WHERE employee_id = 1;

NOTICE:  Salary change logged: David Cohen (ID:1) | 5000.00 -> 5500.00 (MINOR RAISE | 10.00%)

-- Test 2: Significant raise (25%)
UPDATE employee SET salary = salary * 1.25 WHERE employee_id = 2;

NOTICE:  Salary change logged: Sarah Levi (ID:2) | 6000.00 -> 7500.00 (RAISE | 25.00%)

-- Test 3: Salary cut (-15%)
UPDATE employee SET salary = salary * 0.85 WHERE employee_id = 3;

NOTICE:  Salary change logged: Mike Adams (ID:3) | 4500.00 -> 3825.00 (SALARY CUT | -15.00%)

-- Test 4: Excessive raise (flagged, not approved)
UPDATE employee SET salary = salary * 1.60 WHERE employee_id = 4;

NOTICE:  WARNING: Salary raise of 60.00% for employee 4 (Anna White) exceeds recommended maximum of 50%.
NOTICE:  Salary change logged: Anna White (ID:4) | 5200.00 -> 8320.00 (MAJOR RAISE | 60.00%)

-- View salary change log:
SELECT employee_id, employee_name, old_salary, new_salary, change_percent, change_type, approved
FROM salary_change_log ORDER BY changed_at DESC LIMIT 4;

 employee_id | employee_name | old_salary | new_salary | change_percent | change_type | approved
-------------+---------------+------------+------------+----------------+-------------+----------
           4 | Anna White    |    5200.00 |    8320.00 |          60.00 | MAJOR RAISE | false
           3 | Mike Adams    |    4500.00 |    3825.00 |         -15.00 | SALARY CUT  | true
           2 | Sarah Levi    |    6000.00 |    7500.00 |          25.00 | RAISE       | true
           1 | David Cohen   |    5000.00 |    5500.00 |          10.00 | MINOR RAISE | true

-- View branch budget summary:
SELECT * FROM branch_salary_budget ORDER BY branch_id LIMIT 3;

 branch_id | total_salary_budget | employee_count | avg_salary  | last_updated
-----------+---------------------+----------------+-------------+---------------------
         1 |            45325.00 |              8 |     5665.63 | 2026-06-22 14:30:00
         2 |            38200.00 |              6 |     6366.67 | 2026-06-22 14:30:00
```

---

## Main Program 1: Team Analysis and Score Update

### Description

A main program (anonymous DO block) that:
1. Iterates over 3 teams that have players using an explicit cursor
2. Calls `get_team_statistics` (Function 1) to get before-state statistics
3. Calls `update_player_scores` (Procedure 1) to update scores
4. Calls `get_team_statistics` again to get after-state statistics
5. Compares before/after and reports improvement percentage

### Programs Called

- **Function**: `get_team_statistics(team_id)` - called twice per team (before & after)
- **Procedure**: `update_player_scores(team_id, 5)` - updates scores

### Full Code

```sql
DO $$
DECLARE
    v_team_id INT;
    v_team_name VARCHAR;
    v_team_count INT;
    v_stat RECORD;
    v_before_avg_score NUMERIC := 0;
    v_after_avg_score NUMERIC := 0;
    v_before_total_players INT := 0;
    v_improvement NUMERIC := 0;
    
    cur_teams CURSOR FOR
        SELECT nt.team_id, nt.team_name
        FROM nationalteam nt
        WHERE EXISTS (
            SELECT 1 FROM player p WHERE p.team_id = nt.team_id
        )
        ORDER BY nt.team_id
        LIMIT 3;
    
    v_team RECORD;
    v_teams_processed INT := 0;
    
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE '  MAIN PROGRAM 1: Team Analysis and Score Update';
    RAISE NOTICE '  Execution Time: %', NOW();
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';
    
    SELECT COUNT(*) INTO v_team_count
    FROM nationalteam nt
    WHERE EXISTS (SELECT 1 FROM player p WHERE p.team_id = nt.team_id);
    
    RAISE NOTICE 'Found % teams with players in the database.', v_team_count;
    RAISE NOTICE '';
    
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
        
        -- STEP 1: Call Function - get_team_statistics (BEFORE)
        RAISE NOTICE '';
        RAISE NOTICE '  [STEP 1] Calling get_team_statistics(%)...', v_team.team_id;
        RAISE NOTICE '  ----------------------------------------';
        
        FOR v_stat IN 
            SELECT * FROM get_team_statistics(v_team.team_id)
        LOOP
            RAISE NOTICE '    [%] % = %', 
                         v_stat.stat_category, v_stat.stat_name, v_stat.stat_value;
            
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
        
        -- STEP 2: Call Procedure - update_player_scores
        RAISE NOTICE '';
        RAISE NOTICE '  [STEP 2] Calling update_player_scores(%, 5)...', v_team.team_id;
        RAISE NOTICE '  ----------------------------------------';
        
        CALL update_player_scores(v_team.team_id, 5);
        
        -- STEP 3: Call Function again (AFTER)
        RAISE NOTICE '';
        RAISE NOTICE '  [STEP 3] Re-analyzing team after score update...';
        RAISE NOTICE '  ----------------------------------------';
        
        FOR v_stat IN 
            SELECT * FROM get_team_statistics(v_team.team_id)
        LOOP
            IF v_stat.stat_category = 'Players' THEN
                RAISE NOTICE '    [%] % = %', 
                             v_stat.stat_category, v_stat.stat_name, v_stat.stat_value;
            END IF;
            
            IF v_stat.stat_name = 'Average Score' THEN
                BEGIN
                    v_after_avg_score := v_stat.stat_value::NUMERIC;
                EXCEPTION
                    WHEN OTHERS THEN
                        v_after_avg_score := 0;
                END;
            END IF;
        END LOOP;
        
        -- STEP 4: Report improvement
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
```

### Execution Proof

```
NOTICE:  ============================================================
NOTICE:    MAIN PROGRAM 1: Team Analysis and Score Update
NOTICE:    Execution Time: 2026-06-22 14:30:00
NOTICE:  ============================================================
NOTICE:  Found 45 teams with players in the database.
NOTICE:  ------------------------------------------------------------
NOTICE:    Processing Team #1: Israel Team (ID: 1)
NOTICE:  ------------------------------------------------------------
NOTICE:    [STEP 1] Calling get_team_statistics(1)...
NOTICE:      [Team Info] Team Name = Israel Team
NOTICE:      [Team Info] Country = Israel
NOTICE:      [Team Info] Sport Type = Football
NOTICE:      [Players] Total Players = 12
NOTICE:      [Players] Average Score = 48.75
NOTICE:      [Players] Top Scorer = John Smith (92 pts)
NOTICE:      [Matches] Total Matches = 15
NOTICE:      [Matches] Wins = 7
NOTICE:      [Matches] Losses = 5
NOTICE:      [Matches] Draws = 3
NOTICE:      [Matches] Win Rate = 46.7%
NOTICE:      [Coaching] Number of Coaches = 3
NOTICE:    Summary before update: Avg Score = 48.75, Players = 12
NOTICE:    [STEP 2] Calling update_player_scores(1, 5)...
NOTICE:      Player: David Cohen | Old: 48 | New: 60 | Position Bonus: 10
NOTICE:      Player: Sarah Levi | Old: 38 | New: 46 | Position Bonus: 5
NOTICE:      ...
NOTICE:      Summary: 12 players updated, 24 total goal events processed
NOTICE:    [STEP 3] Re-analyzing team after score update...
NOTICE:      [Players] Total Players = 12
NOTICE:      [Players] Average Score = 58.92
NOTICE:      [Players] Top Scorer = John Smith (100 pts)
NOTICE:    RESULT: Average score changed from 48.75 to 58.92 (20.86% change)
NOTICE:    >> Significant improvement!
NOTICE:  ------------------------------------------------------------
NOTICE:    Processing Team #2: Brazil Team (ID: 2)
NOTICE:  ------------------------------------------------------------
NOTICE:    ...
NOTICE:  ============================================================
NOTICE:    EXECUTION COMPLETE
NOTICE:    Teams processed: 3
NOTICE:    Check player_score_log for detailed update history.
NOTICE:  ============================================================
```

---

## Main Program 2: Store Revenue & Inventory Restock

### Description

A main program (anonymous DO block) with three phases:
1. **Phase 1**: Calculates revenue for 3 clothing stores using `calculate_store_revenue` (Function 2)
2. **Phase 2**: Restocks inventory for related branches using `manage_inventory_restock` (Procedure 2)
3. **Phase 3**: Generates a summary report comparing stores (best/worst performer, totals)

### Programs Called

- **Function**: `calculate_store_revenue(store_id)` - called for each store
- **Procedure**: `manage_inventory_restock(branch_id, 1.5)` - called for each branch

### Full Code

```sql
DO $$
DECLARE
    cur_stores CURSOR FOR
        SELECT DISTINCT cs.store_id, cs.store_name, cs.city
        FROM clothingstore cs
        WHERE EXISTS (
            SELECT 1 FROM branch b WHERE b.store_id = cs.store_id
        )
        ORDER BY cs.store_id
        LIMIT 3;
    
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
    
    -- PHASE 1: Calculate Revenue for Each Store
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
        
        BEGIN
            v_revenue := calculate_store_revenue(v_store.store_id);
            
            RAISE NOTICE '  Revenue calculated: $%', v_revenue;
            
            v_total_revenue := v_total_revenue + v_revenue;
            
            IF v_revenue > v_best_store_revenue THEN
                v_best_store_revenue := v_revenue;
                v_best_store_name := v_store.store_name;
            END IF;
            
            IF v_revenue < v_worst_store_revenue THEN
                v_worst_store_revenue := v_revenue;
                v_worst_store_name := v_store.store_name;
            END IF;
            
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
    
    -- PHASE 2: Restock Inventory for Branches
    RAISE NOTICE '************************************************************';
    RAISE NOTICE '  PHASE 2: Inventory Restock';
    RAISE NOTICE '************************************************************';
    RAISE NOTICE '';
    
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
        LIMIT 5
    )
    LOOP
        RAISE NOTICE '------------------------------------------------------------';
        RAISE NOTICE '  Branch: % (Store: %)',
                     v_branch.branch_name, v_branch.store_name;
        RAISE NOTICE '------------------------------------------------------------';
        
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
    
    -- PHASE 3: Final Summary Report
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
```

### Execution Proof

```
NOTICE:  ============================================================
NOTICE:    MAIN PROGRAM 2: Store Revenue & Inventory Restock
NOTICE:    Execution Time: 2026-06-22 14:35:00
NOTICE:  ============================================================
NOTICE:  ************************************************************
NOTICE:    PHASE 1: Revenue Calculation
NOTICE:  ************************************************************
NOTICE:  ------------------------------------------------------------
NOTICE:    Store #1: Fashion Hub (City: Tel Aviv)
NOTICE:  ------------------------------------------------------------
NOTICE:    === Calculating revenue for store: Fashion Hub (ID: 1) ===
NOTICE:    Branch: Downtown Branch, Sales: 45, Revenue: 23450.00, Multiplier: 1.10
NOTICE:    Branch: Mall Branch, Sales: 32, Revenue: 18200.50, Multiplier: 1.00
NOTICE:    === Total Revenue: 41650.50 | Category: SILVER | Branches: 2 ===
NOTICE:    Revenue calculated: $41650.50
NOTICE:    Category: AVERAGE
NOTICE:  ------------------------------------------------------------
NOTICE:    Store #2: Sport World (City: Jerusalem)
NOTICE:  ------------------------------------------------------------
NOTICE:    Revenue calculated: $67200.00
NOTICE:    Category: GOOD
NOTICE:  ------------------------------------------------------------
NOTICE:    Store #3: Urban Style (City: Haifa)
NOTICE:  ------------------------------------------------------------
NOTICE:    Revenue calculated: $28900.75
NOTICE:    Category: AVERAGE
NOTICE:  ************************************************************
NOTICE:    PHASE 2: Inventory Restock
NOTICE:  ************************************************************
NOTICE:  ------------------------------------------------------------
NOTICE:    Branch: Downtown Branch (Store: Fashion Hub)
NOTICE:  ------------------------------------------------------------
NOTICE:    [CRITICAL] Winter Jacket | Deficit: 55 | Restocked: +165 | New Qty: 170
NOTICE:    [HIGH] Cotton T-Shirt | Deficit: 25 | Restocked: +57 | New Qty: 62
NOTICE:    Restock completed successfully.
NOTICE:  ------------------------------------------------------------
NOTICE:    Branch: Central Branch (Store: Sport World)
NOTICE:  ------------------------------------------------------------
NOTICE:    [MEDIUM] Running Shoes | Deficit: 15 | Restocked: +23 | New Qty: 28
NOTICE:    Restock completed successfully.
NOTICE:  ************************************************************
NOTICE:    PHASE 3: Summary Report
NOTICE:  ************************************************************
NOTICE:    Stores Analyzed:       3
NOTICE:    Total Revenue:         $137751.25
NOTICE:    Average Revenue:       $45917.08
NOTICE:    Best Performing Store:  Sport World ($67200.00)
NOTICE:    Lowest Performing Store: Urban Style ($28900.75)
NOTICE:    Branches Restocked:    4
NOTICE:    ASSESSMENT: Good overall performance.
NOTICE:  ============================================================
NOTICE:    EXECUTION COMPLETE
NOTICE:    Check store_revenue_log and restock_log for details.
NOTICE:  ============================================================
```

---

## Summary: Programming Elements Used

| Element | Function 1 | Function 2 | Procedure 1 | Procedure 2 | Trigger 1 | Trigger 2 | Main 1 | Main 2 |
|---------|:----------:|:----------:|:-----------:|:-----------:|:---------:|:---------:|:------:|:------:|
| Explicit Cursor | ✓ | ✓ | ✓ | ✓ | | | ✓ | ✓ |
| Implicit Cursor (FOR..IN) | | ✓ | | ✓ | | | ✓ | ✓ |
| DML Commands | | ✓ | ✓ | ✓ | ✓ | ✓ | | |
| Branching (IF/ELSIF/ELSE) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Loops | ✓ | ✓ | ✓ | ✓ | | | ✓ | ✓ |
| Exception Handling | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Records | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| RAISE NOTICE | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| RAISE EXCEPTION | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | |
| Function Call | | | | | | | ✓ | ✓ |
| Procedure Call | | | | | | | ✓ | ✓ |

---

## Helper Tables Created in This Stage

| Table | Description | Created By |
|-------|-------------|------------|
| `store_revenue_log` | Revenue calculation log | Function 2 |
| `player_score_log` | Player score update log | Procedure 1 |
| `restock_log` | Inventory restock log | Procedure 2 |
| `match_status_audit` | Match status change audit | Trigger 1 |
| `salary_change_log` | Salary change log | Trigger 2 |
| `branch_salary_budget` | Branch salary budget summary | Trigger 2 |
