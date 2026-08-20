# Tests

Run from `databricks-medallion-pipeline/` after `pip install -r requirements.txt`.

## Local (no Databricks)

```bash
python tests/test_sample_data_issues.py
python tests/test_silver_rules_on_csv.py
python tests/test_pipeline_row_relationships.py
```

Or:

```bash
python -m pytest tests/ -q
```

| File | What it proves |
|------|----------------|
| `test_sample_data_issues.py` | Seeded DQ issue **counts** in CSVs |
| `test_silver_rules_on_csv.py` | Same completeness / uniqueness / RI **rules as Silver** flag those rows |
| `test_pipeline_row_relationships.py` | CSV volumes = Bronze contract; prints CE Silver=Bronze / Gold shape checklist |

## Databricks Free / Community Edition

Do **not** run pytest on CE. After Bronze → Silver → Gold:

```sql
SELECT 'b_cust' t, COUNT(*) n FROM bronze.customers
UNION ALL SELECT 's_cust', COUNT(*) FROM silver.customers
UNION ALL SELECT 'b_ord', COUNT(*) FROM bronze.orders
UNION ALL SELECT 's_ord', COUNT(*) FROM silver.orders;
```

Silver counts must match Bronze. Then dashboard queries in `src/dashboard/dashboard_queries.sql`.
