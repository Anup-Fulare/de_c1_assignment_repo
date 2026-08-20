# Debugging Notes

Real issues found while running the pipeline on **Databricks Free/Community Edition**. Reconstructed from git commits after CE test-and-pull cycles. Exact Databricks stack traces were not stored in git; symptoms below match commit messages and diffs.

Sources:

- `303de8b` — Make bronze ingestion Spark Connect-compatible and parameterized (2026-08-19)
- `afe62eb` — Fix data generation to prevent float conversion of integer IDs (2026-08-20)

---

## Issue 1 — Spark Connect / Serverless APIs in Bronze ingest

**Commit:** `303de8b`  
**Files:** `src/bronze/01_ingest_customers.py`, `02_ingest_orders.py`, `03_ingest_products.py`

### Symptom

Bronze ingest that worked as classic Spark-style Python failed on Databricks Free/Community (Spark Connect / serverless): RDD and JVM helpers are not available the same way as on a classic cluster.

### Investigation

Compared first local Bronze (`6f6fa00`) with the CE pull. Original code used:

- `df.rdd.isEmpty()` to reject empty CSVs
- `spark._jvm` / Hadoop `FileSystem` for path checks
- `dbutils.fs.ls` for “file exists”
- Hardcoded `/FileStore/medallion_pipeline/data/...`

Commit message states RDD API is not supported on Spark Connect and JVM accessors are not available on serverless.

### Root cause

AI-generated ingest assumed **classic Spark + DBFS dbutils**. Community/Free compute is **Spark Connect**: no `rdd`, no `_jvm`, and workspace CSV paths are under `/Workspace/Users/{user}/...`, not only `/FileStore/...`.

### Fix (accepted from pull)

- Empty check: `df.limit(1).count() == 0` instead of `rdd.isEmpty()`
- `validate_source`: normalize path only; let `spark.read` fail if the file is missing
- `main()`: auto-detect `/Workspace/Users/{current_user}/ttn_de_c1_assignment_repo_sync/databricks-medallion-pipeline/data/...`
- Fallback `REPO_ROOT` env; widgets still override `source_path`

Raw ingest unchanged: no cleaning, still `bronze.*` Delta overwrite.

### Validation

Re-ran Bronze on CE after pull. Confirmed tables populated (customers ~10010, orders 100000, products 500) without Spark Connect API errors.

### Lesson (validating AI-generated code)

Run generated PySpark on the **same** runtime as submission (CE / Spark Connect), not only “it looks like Databricks.” Reject `rdd` / `_jvm` / `dbutils.fs` unless proven on that cluster.

---

## Issue 2 — Integer IDs written as floats in CSV; Spark IntegerType all-null

**Commit:** `afe62eb`  
**Files:** `src/data_generation/generate_sample_data.py`, `data/orders.csv` (regenerated)

### Symptom

After Bronze on CE, completeness did not match the seeded inventory. Commit message: **all ~100k** `customer_id` / `product_id` values became NULL instead of only 100 / 200 intentional nulls.

### Investigation

Pandas had introduced `pd.NA` for intentional null FKs. Default dtypes promoted integer columns to **float64**, so CSV stored `'5764.0'` instead of `'5764'`. Spark `IntegerType()` on those strings failed (or coerced to null) for every row.

### Root cause

Nullable integer + pandas `NA` → float CSV → Spark integer schema → mass NULL FKs. Silver then looked like “everything fails completeness.”

### Fix (accepted from pull)

- Cast ID/quantity columns to pandas nullable **`Int64`** before `to_csv`
- Applied on products (`product_id`, `stock_quantity`, `reorder_level`), customers (`customer_id`), orders (`order_id`, `customer_id`, `product_id`, `quantity`)
- Regenerated `data/orders.csv` (and related CSVs as needed)

### Validation (per commit message)

Quality metrics / Bronze casts then showed **100** NULL `customer_id` and **200** NULL `product_id`, matching the assignment inventory.

### Lesson

After generating CSVs, spot-check raw file values (`5764` vs `5764.0`) and Spark counts of null FKs **before** trusting Silver. Seeded-issue tests on pandas locally can pass while Spark ingest still breaks.

---

## What we did not invent

- No extra fictional bugs
- `3a7f068` (Silver modules) is implementation of Prompts 14–16, not a CE hotfix — logged under `ai-prompts/silver-layer.md`

---

## Prompt 24 close-out

Silver, Gold, and dashboard queries ran successfully on Databricks CE with **no additional defects** beyond Issues 1–2 above. This file stands as the debugging artifact for submission.

