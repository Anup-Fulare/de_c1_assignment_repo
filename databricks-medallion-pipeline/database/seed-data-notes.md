# Seed Data Notes

## Source files

Generated locally by `src/data_generation/generate_sample_data.py` into:

| File | Approx rows | Role |
|------|-------------|------|
| `data/customers.csv` | 10,010 | Customer master + intentional dups/null emails |
| `data/orders.csv` | 100,000 | Orders + intentional nulls/orphans/dup ids |
| `data/products.csv` | 500 | Clean product catalog |

## CSV → table mapping

| CSV | Bronze table | Silver table |
|-----|--------------|--------------|
| `customers.csv` | `bronze.customers` | `silver.customers` |
| `orders.csv` | `bronze.orders` | `silver.orders` |
| `products.csv` | `bronze.products` | `silver.products` |

Bronze adds `_ingest_source_path` and `_ingest_ts`. Silver adds quality flag columns (see `data-model.md` / `schema.sql`).

## Intentional issues (for Silver tests)

See `src/data_generation/DATA_GENERATION_NOTES.md` and `data-quality-strategy.md`. Verify with:

```bash
python tests/test_sample_data_issues.py
```

## Regenerating seed data

```bash
# from databricks-medallion-pipeline/
python src/data_generation/generate_sample_data.py
python tests/test_sample_data_issues.py
```

Synthetic data only — no real PII.
