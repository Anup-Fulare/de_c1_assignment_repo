-- Dashboard queries — read Gold only (Databricks SQL / Spark SQL).
-- CE: paste each query as a saved SQL query, then add a dashboard tile.
-- Optional filters: uncomment / bind as Databricks SQL parameters where supported.

-- =============================================================================
-- Q1: Top 10 products by revenue (bar chart)
-- Viz: Bar — X = product_name, Y = total_revenue
-- Filter comment: -- AND category = :category
-- =============================================================================
SELECT
  product_id,
  product_name,
  category,
  total_orders,
  total_revenue,
  avg_order_value
FROM gold.sales_by_product
ORDER BY total_revenue DESC
LIMIT 10;


-- =============================================================================
-- Q2: Customer revenue distribution (histogram-friendly bins)
-- Viz: Bar/histogram — X = revenue_bin, Y = customer_count
-- Filter comment: -- AND customer_segment = :segment
-- =============================================================================
SELECT
  CASE
    WHEN total_revenue < 100 THEN '0-99'
    WHEN total_revenue < 250 THEN '100-249'
    WHEN total_revenue < 500 THEN '250-499'
    WHEN total_revenue < 1000 THEN '500-999'
    WHEN total_revenue < 2500 THEN '1000-2499'
    WHEN total_revenue < 5000 THEN '2500-4999'
    ELSE '5000+'
  END AS revenue_bin,
  COUNT(*) AS customer_count,
  CAST(SUM(total_revenue) AS DECIMAL(18, 2)) AS bin_revenue
FROM gold.revenue_by_customer
GROUP BY
  CASE
    WHEN total_revenue < 100 THEN '0-99'
    WHEN total_revenue < 250 THEN '100-249'
    WHEN total_revenue < 500 THEN '250-499'
    WHEN total_revenue < 1000 THEN '500-999'
    WHEN total_revenue < 2500 THEN '1000-2499'
    WHEN total_revenue < 5000 THEN '2500-4999'
    ELSE '5000+'
  END
ORDER BY MIN(total_revenue);


-- =============================================================================
-- Q3: Customer segmentation (pie)
-- Viz: Pie — slice = segment_type, value = customer_count (or total_revenue)
-- Filter comment: -- WHERE segment_type = :segment_type
-- =============================================================================
SELECT
  segment_type,
  customer_count,
  avg_revenue,
  total_revenue
FROM gold.customer_segmentation
ORDER BY segment_type;


-- =============================================================================
-- Q4 (optional extra tile): Daily revenue trend
-- Viz: Line — X = period_start, Y = total_revenue
-- Filter comment: -- AND period_start BETWEEN :start_date AND :end_date
-- =============================================================================
SELECT
  period_start,
  total_orders,
  total_revenue
FROM gold.daily_weekly_trends
WHERE grain = 'day'
ORDER BY period_start;
