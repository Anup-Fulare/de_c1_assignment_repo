# Databricks Medallion Pipeline

Synthetic e-commerce pipeline on **Databricks Free / Community Edition**: CSV → **Bronze** (raw Delta) → **Silver** (flag, do not delete) → **Gold** (aggregations) → **dashboard SQL**.

This folder is the assignment deliverable root. Clone the Git repo, then work inside `databricks-medallion-pipeline/`.

---

## 1. Prerequisites

- Python 3.10+ locally (`pandas` for data generation and tests)
- Databricks Free / Community Edition workspace with a cluster that can write **Delta** tables
- Ability to run `.py` files as notebooks (or paste them into notebooks) and run `%sql`
- Optional: Databricks CLI for DBFS copy — not required if you sync/upload files in the UI

Local Python dependency (pinned in `requirements.txt`):

```text
pandas==2.2.3
```

PySpark and Delta run **on the cluster**, not in this `requirements.txt`.

---

## 2. Clone the repo

```bash
git clone https://github.com/Anup-Fulare/de_c1_assignment_repo.git
cd de_c1_assignment_repo/databricks-medallion-pipeline
```

On Databricks, sync or copy this folder so notebooks can see `data/` and `src/`. The ingest scripts default to a Workspace path of the form:

```text
/Workspace/Users/{your-email}/ttn_de_c1_assignment_repo_sync/databricks-medallion-pipeline/data/
```

If your folder name or user path differs, set the notebook widget `source_path` (per ingest file) or environment variable `REPO_ROOT` to this project directory.

---

## 3. Generate sample data (local)

CSVs may already exist under `data/`. To regenerate (seed `42`):

```bash
cd databricks-medallion-pipeline
pip install -r requirements.txt
python src/data_generation/generate_sample_data.py
python tests/test_sample_data_issues.py
```

| File | Rows | Notes |
|------|------:|--------|
| `data/customers.csv` | 10,010 | 10,000 distinct ids + 10 duplicate `customer_id` rows; 50 null emails |
| `data/orders.csv` | 100,000 | Null FKs, orphans, 20 extra duplicate `order_id` rows |
| `data/products.csv` | 500 | Clean catalog |

Details: `database/seed-data-notes.md`, `src/data_generation/DATA_GENERATION_NOTES.md`.

---

## 4. Put CSVs where Spark can read them

**Path used on Community Edition in this project:** keep CSVs next to the synced repo (`.../databricks-medallion-pipeline/data/*.csv`). Individual Bronze scripts auto-detect `/Workspace/Users/{user}/ttn_de_c1_assignment_repo_sync/databricks-medallion-pipeline/data/...` and allow a `source_path` widget override.

**Optional FileStore / DBFS upload** (if you are not using a Workspace-synced repo):

```text
dbfs:/FileStore/medallion_pipeline/data/customers.csv
dbfs:/FileStore/medallion_pipeline/data/orders.csv
dbfs:/FileStore/medallion_pipeline/data/products.csv
```

Upload via the Databricks file UI, or CLI (tokens stay out of this repo):

```bash
databricks fs mkdirs dbfs:/FileStore/medallion_pipeline/data
databricks fs cp data/customers.csv dbfs:/FileStore/medallion_pipeline/data/customers.csv
databricks fs cp data/orders.csv dbfs:/FileStore/medallion_pipeline/data/orders.csv
databricks fs cp data/products.csv dbfs:/FileStore/medallion_pipeline/data/products.csv
```

`src/bronze/ingest_all.py` defaults to `/FileStore/medallion_pipeline/data`. If CSVs live in the Workspace repo instead, set the `data_dir` widget to that `data` folder (same path the individual scripts use). Spark paths may be written as `/FileStore/...` or `dbfs:/FileStore/...`; ingest normalizes them.

Optional DDL: `database/schema.sql`. Scripts also `CREATE DATABASE IF NOT EXISTS` and `saveAsTable` / `CREATE OR REPLACE TABLE`.

More CE notes: `database/setup-notes.md`. Spark Connect / path issues: `debugging-notes.md`.

---

## 5. Run Bronze → Silver → Gold

Attach a cluster. Run Python files as notebooks (Repos / Workspace), or copy each file into a notebook. Modules that `import_module("01_...")` must sit in the same folder as the orchestrator (`src/bronze`, `src/silver`).

Suggested order:

1. **Bronze (pick one)**
   - `src/bronze/01_ingest_customers.py`
   - `src/bronze/02_ingest_orders.py`
   - `src/bronze/03_ingest_products.py`  
   **or** `src/bronze/ingest_all.py` (set `data_dir` if not using FileStore defaults)
2. **Silver** — `src/silver/create_silver_tables.py`  
   (chains `01_quality_completeness.py` … `05_quality_business_logic.py`; writes `silver.customers|orders|products` and `silver.quality_metrics`)
3. **Gold** — `src/gold/create_gold_tables.py`  
   (runs `01_sales_by_product.sql` … `04_customer_segmentation.sql`)

Expected Bronze row counts (same as CSVs): customers **10010**, orders **100000**, products **500**. Silver row counts match Bronze (flags only; no deletes).

Gold tables:

- `gold.sales_by_product`
- `gold.revenue_by_customer`
- `gold.daily_weekly_trends`
- `gold.customer_segmentation`

Gold uses Silver rows that pass **completeness, uniqueness, and referential integrity** (critical flags false). Revenue uses **Completed** orders only. Segments: Inactive / High-Value (top 20% completed revenue via NTILE) / Repeat / One-Time. See `src/gold/*.sql` and `design-notes.md`.

CE constraints in this codebase: no `rdd` / `_jvm` / `dbutils.fs` path listing; empty tables checked with `df.limit(1).count() == 0`.

---

## 6. Dashboard from `dashboard_queries.sql`

Prereq: Gold tables exist.

1. Open SQL Editor or a notebook `%sql` cell.
2. Confirm `SHOW TABLES IN gold;`
3. Paste queries from `src/dashboard/dashboard_queries.sql` (Gold only):
   - Q1 — top 10 products by revenue (bar)
   - Q2 — customer revenue bins (bar)
   - Q3 — customer segmentation (pie)
   - Q4 — daily trends (`grain = 'day'`, line)
4. Create a SQL dashboard and add tiles, **or** use notebook chart icons if SQL Dashboards are limited on CE.

Step-by-step UI: `src/dashboard/DASHBOARD_GUIDE.md`.  
Example result grids: `src/dashboard/dashboard_queries_sample_result.md`.  
Optional chart images: `src/dashboard/screenshots/`.

This repo does **not** include a Databricks dashboard JSON export or an automated dashboard job.

---

## 7. Run tests

**Local** (from `databricks-medallion-pipeline/`):

```bash
pip install -r requirements.txt
python tests/test_sample_data_issues.py
python tests/test_silver_rules_on_csv.py
python tests/test_pipeline_row_relationships.py
```

`pytest` is optional and is not listed in `requirements.txt`.

**Databricks CE:** do not run pytest on the cluster. After the pipeline:

```sql
SELECT 'b_cust' t, COUNT(*) n FROM bronze.customers
UNION ALL SELECT 's_cust', COUNT(*) FROM silver.customers
UNION ALL SELECT 'b_ord', COUNT(*) FROM bronze.orders
UNION ALL SELECT 's_ord', COUNT(*) FROM silver.orders
UNION ALL SELECT 'b_prod', COUNT(*) FROM bronze.products
UNION ALL SELECT 's_prod', COUNT(*) FROM silver.products;
```

Silver counts must equal Bronze. Then run the dashboard SQL. Details: `tests/README.md`.

---

## 8. Expected outputs and DQ verification

Intentional issues in the CSVs (Silver **flags**, does not drop rows):

| Issue | Seeded count | Silver signal |
|-------|-------------:|---------------|
| Null customer email | 50 | `flag_completeness` |
| Duplicate `customer_id` (extra rows) | 10 extras → **20** rows flagged | `flag_uniqueness` |
| Null `orders.customer_id` | 100 | `flag_completeness` |
| Null `orders.product_id` | 200 | `flag_completeness` |
| Orphan `customer_id` | 50 | `flag_referential_integrity` |
| Orphan `product_id` | 30 | `flag_referential_integrity` |
| Duplicate `order_id` (extra rows) | 20 extras → **40** rows flagged | `flag_uniqueness` |

After Silver, the notebook prints **Intentional issue detection proof** (expected vs actual). Also:

```sql
SELECT check_name, table_name, failed_rows, pct_passed
FROM silver.quality_metrics
ORDER BY check_name, table_name;
```

Dashboard sanity (after Gold): Q1 returns **10** rows; Q3 typically **four** segment types. Strategy write-up: `data-quality-strategy.md`.

---

## 9. Project structure

```text
databricks-medallion-pipeline/
  README.md
  candidate-info.md
  requirements-analysis.md
  design-notes.md
  data-model.md
  data-quality-strategy.md
  tool-workflow.md
  debugging-notes.md
  reflection.md
  final-ai-usage-summary.md
  requirements.txt
  .cursorrules
  data/                          # generated CSVs
  database/                      # schema.sql, setup-notes, seed-data-notes
  src/data_generation/           # generate_sample_data.py
  src/bronze/                    # ingest scripts + ingest_all.py
  src/silver/                    # quality 01–05 + create_silver_tables.py
  src/gold/                      # four .sql files + create_gold_tables.py
  src/dashboard/                 # dashboard_queries.sql, DASHBOARD_GUIDE.md
  tests/
  ai-prompts/                    # Cursor prompt history
  tool-specific/cursor-workflow/
```

---

## 10. Responsible AI / no real PII

- All customer names, emails, and ids are **synthetic** (generator seed 42).
- Do not commit workspace tokens, PATs, cluster credentials, or `.env` files.
- Do not replace sample CSVs with production extracts.
- Silver keeps bad rows for audit; Gold excludes critical-flag failures from KPIs.

Candidate metadata: `candidate-info.md`. AI usage history: `ai-prompts/`. Runtime fixes: `debugging-notes.md`.
