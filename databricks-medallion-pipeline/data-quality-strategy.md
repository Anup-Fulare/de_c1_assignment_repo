# Data Quality Strategy

## Quality Checks Overview

### 1. Completeness Check

- **What:** No NULLs in critical fields
- **How:** Count NULLs in `customers.email`, `orders.customer_id`, `orders.product_id`
- **Threshold:** >99% complete
- **Result:** Flag rows with NULLs (`flag_completeness = true`); do not delete

### 2. Uniqueness Check

- **What:** No duplicate business keys
- **How:** Detect duplicate `customer_id` and duplicate `order_id`
- **Threshold:** 100% unique
- **Result:** Flag duplicate rows (`flag_uniqueness = true`); do not delete

### 3. Type Validation

- **What:** Types, ranges, and allowed values are valid when present
- **How:** Examples — email format when not null; `quantity` / prices ≥ 0; `order_status` in Allowed set; dates parseable; `customer_segment` in Premium/Standard/Basic
- **Threshold:** >99% valid
- **Result:** Flag invalid rows (`flag_type_validation = true`); do not delete

### 4. Referential Integrity

- **What:** Non-null FKs exist in parent tables
- **How:** `orders.customer_id` ∈ `customers.customer_id`; `orders.product_id` ∈ `products.product_id` (when FK not null)
- **Threshold:** >99.9% valid
- **Result:** Flag orphan rows (`flag_referential_integrity = true`); do not delete

### 5. Business Logic

- **What:** Domain rules hold
- **How:** Examples — `total_amount ≈ quantity * unit_price` (small tolerance); `payment_date` null allowed for Pending/Cancelled; Completed preferably has payment_date; `signup_date` not far in the future
- **Threshold:** >99% valid (report-focused; flag all failures)
- **Result:** Flag rule failures (`flag_business_logic = true`); do not delete

## Row-level result

- `quality_check_result = PASS` only if all applicable flags are false
- Otherwise `FAIL` (and optional `quality_failure_reasons`)

## Quality Metrics Report

Persisted to **`silver.quality_metrics`** by `src/silver/create_silver_tables.py` after each Silver run.

| check_name | table_name | total_rows_evaluated | failed_rows | pct_passed | report_ts |
|------------|------------|----------------------|-------------|------------|-----------|
| completeness | customers / orders | row count | flagged count | (total−failed)/total×100 | run time |
| uniqueness | customers / orders | … | … | … | … |
| type_validation | customers / orders / products | … | … | … | … |
| referential_integrity | orders | … | … | … | … |
| business_logic | customers / orders | … | … | … | … |

**Console output** also prints:
- Per-table Silver row counts and FAIL row counts
- `silver.quality_metrics` contents (`show`)
- **Intentional issue detection proof** — compares actual counts to seeded inventory (50 null emails, 20 dup customer rows flagged, etc.)

**Overall Silver row result:** `quality_check_result` = PASS only if all applicable `flag_*` columns are false; otherwise FAIL with `quality_failure_reasons` (pipe-separated check codes).

Example query after run:

```sql
SELECT check_name, table_name, failed_rows, pct_passed
FROM silver.quality_metrics
ORDER BY check_name, table_name;
```

## Sample Data Quality Issues (intentional inventory)

**customers.csv**

| Issue | Count |
|-------|------:|
| NULL email | 50 |
| Duplicate customer_id | 10 |

**orders.csv**

| Issue | Count |
|-------|------:|
| NULL customer_id | 100 |
| NULL product_id | 200 |
| customer_id not in customers | 50 |
| product_id not in products | 30 |
| Duplicate order_id | 20 |

**products.csv:** clean catalog (0 intentional issues)

**Total intentional issues:** ~700 problematic rows out of ~100,000+ (≈0.7%)

Silver checks must surface these counts (within how duplicates/orphans are counted) so tests can assert detection.

## Gold feed rule (reminder)

Gold uses rows that pass critical checks for join/aggregation keys; Silver retains flagged rows for transparency.
