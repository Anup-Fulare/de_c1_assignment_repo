# Data Generation Notes

## Purpose

Create synthetic e-commerce CSVs for the medallion pipeline so Bronze can ingest raw files and Silver can demonstrate data-quality checks against **known** bad rows.

## How data is generated

- Script: `src/data_generation/generate_sample_data.py`
- Stack: Python stdlib `random` + `pandas` (no Faker; keeps dependencies light)
- Reproducible seed: `SEED = 42`
- Run from `databricks-medallion-pipeline/`:

```bash
python src/data_generation/generate_sample_data.py
```

## Volumes

| File | Target |
|------|--------|
| `data/products.csv` | 500 rows (clean) |
| `data/customers.csv` | 10,000 unique + 10 intentional duplicate rows |
| `data/orders.csv` | 100,000 rows |

## Why intentional quality issues exist

Silver must prove it can **flag** (not delete) realistic problems. Exact counts match the assignment:

| Source | Issue | Count |
|--------|--------|------:|
| customers | NULL email | 50 |
| customers | duplicate `customer_id` (extra rows) | 10 |
| orders | NULL `customer_id` | 100 |
| orders | NULL `product_id` | 200 |
| orders | `customer_id` not in customers | 50 |
| orders | `product_id` not in products | 30 |
| orders | duplicate `order_id` (extra rows sharing an id) | 20 |

Products remain a clean reference catalog for referential-integrity checks.

## Injection approach

- Issue slices on orders are drawn from a shuffled index so the intentional bad rows are largely **disjoint**.
- Duplicate customers are **appended** copies of `customer_id` 1–10 (name suffix `(dup)`).
- Duplicate orders overwrite `order_id` on 20 rows to equal another row’s `order_id`.
- Orphan FKs use ids outside the valid ranges (`N_CUSTOMERS + 10000+`, `N_PRODUCTS + 10000+`).

## Verification

The script prints a verification summary after write. Prompt 8 adds formal asserts on these counts.
