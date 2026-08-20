-- Gold: revenue by customer
-- Databricks SQL / Spark SQL (CE). No rdd / JVM.
--
-- Silver → Gold filter: orders pass completeness + uniqueness + RI.
-- Revenue: Completed orders only.
-- lifetime_value_actual = SUM(total_amount) of those completed orders (not source lifetime_value).
-- Customers: exclude uniqueness failures so duplicate customer_id rows do not double-count.

CREATE OR REPLACE TABLE gold.revenue_by_customer
USING DELTA AS
SELECT
  c.customer_id,
  MAX(c.customer_name) AS customer_name,
  MAX(c.customer_segment) AS customer_segment,
  COUNT(*) AS total_orders,
  CAST(SUM(o.total_amount) AS DECIMAL(18, 2)) AS total_revenue,
  CAST(AVG(o.total_amount) AS DECIMAL(18, 2)) AS avg_order_value,
  CAST(SUM(o.total_amount) AS DECIMAL(18, 2)) AS lifetime_value_actual
FROM silver.customers c
INNER JOIN silver.orders o
  ON c.customer_id = o.customer_id
WHERE COALESCE(c.flag_uniqueness, false) = false
  AND COALESCE(c.flag_completeness, false) = false
  AND COALESCE(o.flag_completeness, false) = false
  AND COALESCE(o.flag_uniqueness, false) = false
  AND COALESCE(o.flag_referential_integrity, false) = false
  AND o.order_status = 'Completed'
GROUP BY c.customer_id;
