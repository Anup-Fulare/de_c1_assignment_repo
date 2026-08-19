# Design Notes

## Architecture Overview

```text
CSV (local generate) → DBFS upload → Bronze (raw Delta)
                                  → Silver (flagged DQ + metrics)
                                  → Gold (4 aggregations)
                                  → Databricks SQL Dashboard (3+ tiles)
```

Project root for deliverables: `databricks-medallion-pipeline/`. Layers stay separated: Bronze never cleans; Silver never silently deletes; Gold only aggregates from documented Silver filters; Dashboard reads Gold only.

## Data Model & Schema

Three sources: `customers`, `orders`, `products` (schemas in [data-model.md](data-model.md)). Silver adds quality flags / `quality_check_result`. Bronze may add light ingestion metadata columns without changing business values.

## Bronze Layer Design

- Scripts: `src/bronze/01_ingest_customers.py`, `02_ingest_orders.py`, `03_ingest_products.py`, `ingest_all.py`
- Read CSVs from configurable DBFS paths; write Delta tables `bronze.customers`, `bronze.orders`, `bronze.products`
- Cast types for storage; do not drop or fix bad rows
- Log source path, row count, ingestion timestamp; fail clearly if path missing/empty

## Silver Layer Design

- Modules: completeness, uniqueness, type validation, referential integrity, business logic + `create_silver_tables.py`
- Read Bronze; apply checks; write Silver tables with flag columns
- Emit quality metrics report (% passed per check)
- Must detect intentional seeded issues from sample data (~700 bad rows)

## Gold Layer Design

Four tables (SQL under `src/gold/` + `create_gold_tables.py`):

| Table | Purpose |
|-------|---------|
| sales_by_product | orders, revenue, AOV by product |
| revenue_by_customer | orders, revenue, AOV, lifetime_value_actual |
| daily_weekly_trends | revenue/order trends by day and week |
| customer_segmentation | High-Value / Repeat / One-Time / Inactive counts & revenue |

**Silver → Gold filter:** Gold analytics use rows that pass critical checks (completeness + uniqueness + referential integrity for join keys). Flagged/failed rows remain in Silver for audit; they are not deleted.

**Segment draft rules (locked in SQL comments later):**
- High-Value: top revenue cohort among customers with ≥1 completed order (e.g. top 20% by revenue or threshold)
- Repeat: ≥2 completed orders, not High-Value
- One-Time: exactly 1 completed order
- Inactive: zero completed orders in the dataset window (may include cancelled-only)

## Data Quality Validation Strategy

See [data-quality-strategy.md](data-quality-strategy.md). Principle: **flag, don’t delete**. Thresholds guide the report; all bad rows stay in Silver with results.

## Debugging Approach

1. Reproduce with row counts / printed metrics vs expected intentional issue counts
2. Spot-check sample bad IDs in CSV vs Silver flags
3. Compare Gold totals to manual `SUM`/`COUNT` on filtered Silver
4. Record symptom → root cause → fix → validation in `debugging-notes.md` and `ai-prompts/debugging.md`
5. Prefer fixing detection logic or docs over “cleaning away” the seeded issues
