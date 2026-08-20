-- Gold: sales by product
-- Databricks SQL / Spark SQL (Free/Community Edition). No rdd / JVM.
--
-- Silver → Gold filter (design-notes.md):
--   Orders must pass critical checks for join keys:
--     flag_completeness = false
--     flag_uniqueness = false
--     flag_referential_integrity = false
--   Revenue uses Completed orders only (business-ready).
--   Products: uniqueness flag false (catalog is clean).
-- Flagged Silver rows stay in Silver; they are excluded here, not deleted.

CREATE OR REPLACE TABLE gold.sales_by_product
USING DELTA AS
SELECT
  p.product_id,
  p.product_name,
  p.category,
  COUNT(*) AS total_orders,
  CAST(SUM(o.total_amount) AS DECIMAL(18, 2)) AS total_revenue,
  CAST(AVG(o.total_amount) AS DECIMAL(18, 2)) AS avg_order_value
FROM silver.orders o
INNER JOIN silver.products p
  ON o.product_id = p.product_id
WHERE COALESCE(o.flag_completeness, false) = false
  AND COALESCE(o.flag_uniqueness, false) = false
  AND COALESCE(o.flag_referential_integrity, false) = false
  AND COALESCE(p.flag_uniqueness, false) = false
  AND o.order_status = 'Completed'
GROUP BY p.product_id, p.product_name, p.category;
