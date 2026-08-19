# Setup Notes (Databricks Free / Community Edition)

## Prerequisites

- Databricks Free/Community Edition workspace
- Cluster with Spark runtime that supports Delta
- This repo cloned (or files uploaded) so you can access `databricks-medallion-pipeline/`

## 1. Generate CSVs locally (if not already present)

```bash
cd databricks-medallion-pipeline
pip install -r requirements.txt
python src/data_generation/generate_sample_data.py
python tests/test_sample_data_issues.py
```

## 2. Upload CSVs to DBFS

Suggested path (adjust to your username/workspace):

```text
dbfs:/FileStore/medallion_pipeline/data/customers.csv
dbfs:/FileStore/medallion_pipeline/data/orders.csv
dbfs:/FileStore/medallion_pipeline/data/products.csv
```

Options:

- Databricks UI: **Data** / **Catalog** → Upload, or **DBFS** file browser under `/FileStore/...`
- Databricks CLI (if configured; no secrets in this repo):

```bash
databricks fs mkdirs dbfs:/FileStore/medallion_pipeline/data
databricks fs cp data/customers.csv dbfs:/FileStore/medallion_pipeline/data/customers.csv
databricks fs cp data/orders.csv dbfs:/FileStore/medallion_pipeline/data/orders.csv
databricks fs cp data/products.csv dbfs:/FileStore/medallion_pipeline/data/products.csv
```

## 3. Create databases / tables (optional explicit DDL)

In a Databricks SQL / notebook cell, run statements from `database/schema.sql`, or let Bronze/Silver/Gold scripts `saveAsTable` / `createOrReplace`.

## 4. Run pipeline order

1. Bronze: `src/bronze/01_ingest_*.py` or `ingest_all.py` (paths pointed at DBFS above)
2. Silver: quality modules + `create_silver_tables.py`
3. Gold: SQL / `create_gold_tables.py`
4. Dashboard: queries in `src/dashboard/dashboard_queries.sql`

Point ingest widgets/parameters at:

```text
/FileStore/medallion_pipeline/data
```

(or `dbfs:/FileStore/medallion_pipeline/data` depending on API).

## 5. Security

- Do not store workspace tokens, passwords, or personal access tokens in this repository
- Use synthetic CSVs only

## CE quirks

- Default metastore naming may be `hive_metastore.bronze.*` in some UIs
- If `CREATE DATABASE` fails, create schemas via UI or write Delta to a DBFS path and register tables later
- Keep paths simple; avoid proprietary cloud features not available on CE
