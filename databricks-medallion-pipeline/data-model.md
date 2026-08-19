# Data Model

## Source schemas (CSV)

### customers

| Column | Type | Notes |
|--------|------|--------|
| customer_id | INT | PK |
| customer_name | STRING | |
| email | STRING | nullable in intentional bad rows |
| country | STRING | |
| signup_date | DATE | |
| customer_segment | STRING | Premium / Standard / Basic |
| lifetime_value | DECIMAL | source attribute |

**Volume:** ~10,000 rows

### orders

| Column | Type | Notes |
|--------|------|--------|
| order_id | INT | PK (duplicates intentional in sample) |
| customer_id | INT | FK → customers (nullable / orphan intentional) |
| order_date | DATE | |
| product_id | INT | FK → products (nullable / orphan intentional) |
| quantity | INT | |
| unit_price | DECIMAL | |
| total_amount | DECIMAL | |
| order_status | STRING | Pending / Completed / Cancelled |
| payment_date | DATE | nullable |

**Volume:** ~100,000 rows

### products

| Column | Type | Notes |
|--------|------|--------|
| product_id | INT | PK |
| product_name | STRING | |
| category | STRING | |
| price | DECIMAL | |
| cost | DECIMAL | |
| stock_quantity | INT | |
| reorder_level | INT | |

**Volume:** ~500 rows (clean reference catalog)

## Keys & relationships

- `customers.customer_id` 1→N `orders.customer_id`
- `products.product_id` 1→N `orders.product_id`
- Sample data intentionally breaks some relationships for Silver RI tests

## Bronze layer columns

Same business columns as source, plus optional metadata:

| Column | Type | Notes |
|--------|------|--------|
| _ingest_source_path | STRING | CSV path |
| _ingest_ts | TIMESTAMP | ingestion time |

No rows removed; raw values preserved.

## Silver layer columns

All Bronze business columns, plus:

| Column | Type | Notes |
|--------|------|--------|
| quality_check_result | STRING | e.g. PASS / FAIL |
| flag_completeness | BOOLEAN | |
| flag_uniqueness | BOOLEAN | |
| flag_type_validation | BOOLEAN | |
| flag_referential_integrity | BOOLEAN | |
| flag_business_logic | BOOLEAN | |
| quality_failure_reasons | STRING | optional pipe-delimited codes |

Flagged rows are retained.

## Gold layer outputs (logical)

### gold.sales_by_product
`product_id`, `product_name`, `category`, `total_orders`, `total_revenue`, `avg_order_value`

### gold.revenue_by_customer
`customer_id`, `customer_name`, `customer_segment`, `total_orders`, `total_revenue`, `avg_order_value`, `lifetime_value_actual`

### gold.daily_weekly_trends
Daily grain: `order_date`, `total_orders`, `total_revenue`  
Weekly grain: `week_start`, `total_orders`, `total_revenue` (or equivalent week key)

### gold.customer_segmentation
`segment_type`, `customer_count`, `avg_revenue`, `total_revenue`  
`segment_type` ∈ High-Value, Repeat, One-Time, Inactive

## Naming convention

- Schemas/databases: `bronze`, `silver`, `gold` (CE-friendly; adjust in setup notes if workspace uses catalog prefixes)
