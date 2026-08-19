-- Databricks / Delta-friendly schema for medallion pipeline
-- Free/Community Edition: use hive_metastore (or default) databases.
-- Adjust catalog prefixes if your workspace uses Unity Catalog.

-- =============================================================================
-- Databases
-- =============================================================================
CREATE DATABASE IF NOT EXISTS bronze;
CREATE DATABASE IF NOT EXISTS silver;
CREATE DATABASE IF NOT EXISTS gold;

-- =============================================================================
-- Bronze: raw ingest (business columns + optional ingest metadata)
-- =============================================================================

CREATE TABLE IF NOT EXISTS bronze.customers (
  customer_id INT,
  customer_name STRING,
  email STRING,
  country STRING,
  signup_date DATE,
  customer_segment STRING,
  lifetime_value DECIMAL(18, 2),
  _ingest_source_path STRING,
  _ingest_ts TIMESTAMP
)
USING DELTA;

CREATE TABLE IF NOT EXISTS bronze.orders (
  order_id INT,
  customer_id INT,
  order_date DATE,
  product_id INT,
  quantity INT,
  unit_price DECIMAL(18, 2),
  total_amount DECIMAL(18, 2),
  order_status STRING,
  payment_date DATE,
  _ingest_source_path STRING,
  _ingest_ts TIMESTAMP
)
USING DELTA;

CREATE TABLE IF NOT EXISTS bronze.products (
  product_id INT,
  product_name STRING,
  category STRING,
  price DECIMAL(18, 2),
  cost DECIMAL(18, 2),
  stock_quantity INT,
  reorder_level INT,
  _ingest_source_path STRING,
  _ingest_ts TIMESTAMP
)
USING DELTA;

-- =============================================================================
-- Silver: same business grain + quality flags (flag, do not delete)
-- =============================================================================

CREATE TABLE IF NOT EXISTS silver.customers (
  customer_id INT,
  customer_name STRING,
  email STRING,
  country STRING,
  signup_date DATE,
  customer_segment STRING,
  lifetime_value DECIMAL(18, 2),
  _ingest_source_path STRING,
  _ingest_ts TIMESTAMP,
  quality_check_result STRING,
  flag_completeness BOOLEAN,
  flag_uniqueness BOOLEAN,
  flag_type_validation BOOLEAN,
  flag_referential_integrity BOOLEAN,
  flag_business_logic BOOLEAN,
  quality_failure_reasons STRING
)
USING DELTA;

CREATE TABLE IF NOT EXISTS silver.orders (
  order_id INT,
  customer_id INT,
  order_date DATE,
  product_id INT,
  quantity INT,
  unit_price DECIMAL(18, 2),
  total_amount DECIMAL(18, 2),
  order_status STRING,
  payment_date DATE,
  _ingest_source_path STRING,
  _ingest_ts TIMESTAMP,
  quality_check_result STRING,
  flag_completeness BOOLEAN,
  flag_uniqueness BOOLEAN,
  flag_type_validation BOOLEAN,
  flag_referential_integrity BOOLEAN,
  flag_business_logic BOOLEAN,
  quality_failure_reasons STRING
)
USING DELTA;

CREATE TABLE IF NOT EXISTS silver.products (
  product_id INT,
  product_name STRING,
  category STRING,
  price DECIMAL(18, 2),
  cost DECIMAL(18, 2),
  stock_quantity INT,
  reorder_level INT,
  _ingest_source_path STRING,
  _ingest_ts TIMESTAMP,
  quality_check_result STRING,
  flag_completeness BOOLEAN,
  flag_uniqueness BOOLEAN,
  flag_type_validation BOOLEAN,
  flag_referential_integrity BOOLEAN,
  flag_business_logic BOOLEAN,
  quality_failure_reasons STRING
)
USING DELTA;

-- Optional metrics table for quality report
CREATE TABLE IF NOT EXISTS silver.quality_metrics (
  check_name STRING,
  table_name STRING,
  total_rows_evaluated BIGINT,
  failed_rows BIGINT,
  pct_passed DOUBLE,
  report_ts TIMESTAMP
)
USING DELTA;

-- =============================================================================
-- Gold: analytics aggregations
-- =============================================================================

CREATE TABLE IF NOT EXISTS gold.sales_by_product (
  product_id INT,
  product_name STRING,
  category STRING,
  total_orders BIGINT,
  total_revenue DECIMAL(18, 2),
  avg_order_value DECIMAL(18, 2)
)
USING DELTA;

CREATE TABLE IF NOT EXISTS gold.revenue_by_customer (
  customer_id INT,
  customer_name STRING,
  customer_segment STRING,
  total_orders BIGINT,
  total_revenue DECIMAL(18, 2),
  avg_order_value DECIMAL(18, 2),
  lifetime_value_actual DECIMAL(18, 2)
)
USING DELTA;

CREATE TABLE IF NOT EXISTS gold.daily_weekly_trends (
  grain STRING,              -- 'day' or 'week'
  period_start DATE,         -- order_date or week_start
  total_orders BIGINT,
  total_revenue DECIMAL(18, 2)
)
USING DELTA;

CREATE TABLE IF NOT EXISTS gold.customer_segmentation (
  segment_type STRING,       -- High-Value / Repeat / One-Time / Inactive
  customer_count BIGINT,
  avg_revenue DECIMAL(18, 2),
  total_revenue DECIMAL(18, 2)
)
USING DELTA;

-- Notes for CE:
-- * If CREATE DATABASE is restricted, use spark.sql("CREATE SCHEMA IF NOT EXISTS ...")
--   or write to paths like /user/hive/warehouse/bronze.db/...
-- * Ingest scripts may use createOrReplace / saveAsTable instead of running this file first.
