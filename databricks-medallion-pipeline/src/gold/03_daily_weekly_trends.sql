-- Gold: daily and weekly revenue / order trends
-- Databricks SQL / Spark SQL (CE). No rdd / JVM.
--
-- grain = 'day'  → period_start = order_date
-- grain = 'week' → period_start = date_trunc('WEEK', order_date)  (Monday week start in Spark)
-- Same Silver critical-check filter + Completed orders as other Gold facts.

CREATE OR REPLACE TABLE gold.daily_weekly_trends
USING DELTA AS
WITH completed AS (
  SELECT
    o.order_date,
    o.total_amount
  FROM silver.orders o
  WHERE COALESCE(o.flag_completeness, false) = false
    AND COALESCE(o.flag_uniqueness, false) = false
    AND COALESCE(o.flag_referential_integrity, false) = false
    AND o.order_status = 'Completed'
    AND o.order_date IS NOT NULL
),
daily AS (
  SELECT
    'day' AS grain,
    order_date AS period_start,
    COUNT(*) AS total_orders,
    CAST(SUM(total_amount) AS DECIMAL(18, 2)) AS total_revenue
  FROM completed
  GROUP BY order_date
),
weekly AS (
  SELECT
    'week' AS grain,
    CAST(date_trunc('WEEK', order_date) AS DATE) AS period_start,
    COUNT(*) AS total_orders,
    CAST(SUM(total_amount) AS DECIMAL(18, 2)) AS total_revenue
  FROM completed
  GROUP BY date_trunc('WEEK', order_date)
)
SELECT grain, period_start, total_orders, total_revenue FROM daily
UNION ALL
SELECT grain, period_start, total_orders, total_revenue FROM weekly;
