-- ==========================================
-- Views.sql
-- Stage C - Views and Queries
-- ==========================================

-- View 1: Original sports side
CREATE OR REPLACE VIEW vw_store_tournaments AS
SELECT
    cs.store_id,
    cs.store_name,
    t.tournament_id,
    t.season,
    t.start_date,
    t.end_date,
    t.location
FROM clothingstore cs
JOIN tournament t
    ON cs.store_id = t.store_id;

-- Query 1 on View 1
SELECT *
FROM vw_store_tournaments
LIMIT 10;

-- Query 2 on View 1
SELECT
    store_name,
    COUNT(tournament_id) AS number_of_tournaments
FROM vw_store_tournaments
GROUP BY store_name;


-- View 2: Received clothing-store side
CREATE OR REPLACE VIEW vw_branch_sales AS
SELECT
    b.branch_id,
    b.branch_name,
    cs.store_name,
    s.sale_id,
    s.sale_date,
    s.total_amount
FROM branch b
JOIN clothingstore cs
    ON b.store_id = cs.store_id
JOIN sale s
    ON b.branch_id = s.branch_id;

-- Query 1 on View 2
SELECT *
FROM vw_branch_sales
LIMIT 10;

-- Query 2 on View 2
SELECT
    branch_name,
    COUNT(sale_id) AS number_of_sales,
    SUM(total_amount) AS total_sales_amount
FROM vw_branch_sales
GROUP BY branch_name
ORDER BY total_sales_amount DESC;