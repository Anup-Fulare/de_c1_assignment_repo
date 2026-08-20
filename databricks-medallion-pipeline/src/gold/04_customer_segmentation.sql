-- Gold: customer segmentation
-- Databricks SQL / Spark SQL (CE). No rdd / JVM.
--
-- Segment rules (design-notes.md):
--   High-Value : customers with ≥1 completed order AND in top 20% by completed revenue (NTILE 5, bucket 1)
--   Repeat     : ≥2 completed orders, not High-Value
--   One-Time   : exactly 1 completed order, not High-Value
--   Inactive   : 0 completed orders in the dataset (includes cancelled-only / never completed)
--
-- Base customers: uniqueness + completeness pass (one row per customer_id).
-- Completed orders: same critical flags as other Gold tables.

CREATE OR REPLACE TABLE gold.customer_segmentation
USING DELTA AS
WITH eligible_customers AS (
  SELECT DISTINCT customer_id
  FROM silver.customers
  WHERE COALESCE(flag_uniqueness, false) = false
    AND COALESCE(flag_completeness, false) = false
),
completed AS (
  SELECT
    o.customer_id,
    o.total_amount
  FROM silver.orders o
  WHERE COALESCE(o.flag_completeness, false) = false
    AND COALESCE(o.flag_uniqueness, false) = false
    AND COALESCE(o.flag_referential_integrity, false) = false
    AND o.order_status = 'Completed'
),
cust_stats AS (
  SELECT
    e.customer_id,
    COUNT(c.total_amount) AS completed_orders,
    CAST(COALESCE(SUM(c.total_amount), 0) AS DECIMAL(18, 2)) AS completed_revenue
  FROM eligible_customers e
  LEFT JOIN completed c
    ON e.customer_id = c.customer_id
  GROUP BY e.customer_id
),
ranked AS (
  SELECT
    customer_id,
    completed_orders,
    completed_revenue,
    CASE
      WHEN completed_orders >= 1 THEN NTILE(5) OVER (
        PARTITION BY CASE WHEN completed_orders >= 1 THEN 1 ELSE 0 END
        ORDER BY completed_revenue DESC
      )
      ELSE NULL
    END AS revenue_quintile
  FROM cust_stats
),
labeled AS (
  SELECT
    customer_id,
    completed_orders,
    completed_revenue,
    CASE
      WHEN completed_orders = 0 THEN 'Inactive'
      WHEN revenue_quintile = 1 THEN 'High-Value'
      WHEN completed_orders >= 2 THEN 'Repeat'
      WHEN completed_orders = 1 THEN 'One-Time'
      ELSE 'Inactive'
    END AS segment_type
  FROM ranked
)
SELECT
  segment_type,
  COUNT(*) AS customer_count,
  CAST(AVG(completed_revenue) AS DECIMAL(18, 2)) AS avg_revenue,
  CAST(SUM(completed_revenue) AS DECIMAL(18, 2)) AS total_revenue
FROM labeled
GROUP BY segment_type;
