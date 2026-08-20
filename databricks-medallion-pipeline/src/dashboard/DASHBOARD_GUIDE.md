# Dashboard Guide

Databricks **Free / Community Edition** — SQL queries and tiles over **Gold** tables only.  
Prereq: `gold.sales_by_product`, `gold.revenue_by_customer`, `gold.customer_segmentation`, `gold.daily_weekly_trends` exist (run `src/gold/create_gold_tables.py` first).

SQL text: [`dashboard_queries.sql`](dashboard_queries.sql)

---

## 1. Open SQL

1. Start (or attach) a cluster that can query the `gold` schema.
2. Open **SQL Editor** (or a notebook cell with `%sql`).
3. Confirm:

```sql
SHOW TABLES IN gold;
```

---

## 2. Save the queries

Create **at least three** saved queries (paste from `dashboard_queries.sql`):

| Query | Gold source | Suggested chart |
|--------|-------------|-----------------|
| Top 10 products by revenue | `gold.sales_by_product` | **Bar** |
| Customer revenue distribution | binned `gold.revenue_by_customer` | **Bar** (histogram-style) |
| Customer segmentation | `gold.customer_segmentation` | **Pie** |
| Optional: daily trend | `gold.daily_weekly_trends` where `grain = 'day'` | **Line** |

Run each query once and confirm rows return.

**Parameters (if your SQL Editor supports them):** comments in the SQL file show `:category`, `:segment`, `:start_date` / `:end_date`. On CE, if named parameters are missing, keep filters commented or hardcode a test filter.

---

## 3. Create a dashboard

UI names vary slightly on Free vs workspace SQL:

1. **Dashboards** (or **SQL Dashboards**) → **Create dashboard**.
2. Name it e.g. `E-commerce Gold — Sales overview`.
3. **Add visualization / tile** for each saved query:
   - **Bar:** Top 10 — X = `product_name`, Y = `total_revenue`
   - **Bar:** Revenue bins — X = `revenue_bin`, Y = `customer_count`
   - **Pie:** Segmentation — name = `segment_type`, value = `customer_count` (or `total_revenue`)
   - Optional **Line:** Daily — X = `period_start`, Y = `total_revenue`

4. Optional dashboard filters: date range (daily tile), product category, segment.

---

## 4. If SQL Dashboards are not available on CE

Use a **notebook**:

1. `%sql` cells with the same three queries.
2. Chart icon on the result grid → Bar / Pie / Line.
3. Screenshot or export for reviewers; note this fallback in your submission if the Dashboard product is limited.

---

## 5. Publish / share

- **CE:** sharing may be limited to your account. Document that the dashboard lives in your workspace and queries read `gold.*`.
- Do **not** put workspace tokens or personal access tokens in this repo.
- For the assignment, a working query set + this guide + tiles (or notebook charts) is enough.

---

## 6. Quick sanity checks

- Top 10: 10 rows, descending revenue.
- Pie: four slices High-Value / Repeat / One-Time / Inactive (same as Gold test).
- Bins: `customer_count` sums to `SELECT COUNT(*) FROM gold.revenue_by_customer`.
