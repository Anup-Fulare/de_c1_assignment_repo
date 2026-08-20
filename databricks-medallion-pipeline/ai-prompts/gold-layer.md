# AI Prompts — Gold Layer

## How to use this file

Append real Cursor iterations for Gold aggregations and table creation. Do not invent prompt history after the fact.

---

## Prompt 1: Four aggregation SQL files (playbook Prompt 18)

**PROMPT SENT:**

Implement Gold SQL: sales_by_product, revenue_by_customer, daily_weekly_trends, customer_segmentation (High-Value / Repeat / One-Time / Inactive). Spark SQL / Databricks SQL, CE-safe. Silver source; document quality-flag filter. Match design-notes.md.

**AI RESPONSE SUMMARY:**

Wrote four `CREATE OR REPLACE TABLE gold.* USING DELTA AS` scripts. Filter: orders pass completeness + uniqueness + RI; Completed only for revenue. Segmentation: Inactive = 0 completed; High-Value = top 20% (NTILE 5) among those with ≥1 completed; Repeat ≥2 not HV; One-Time = 1 not HV. Comments document Silver→Gold rules.

**YOUR EVALUATION:**

- Accepted (why): Matches assignment columns and design segment rules; no rdd/JVM; flagged rows excluded not deleted.
- Changed (why): Used Completed-only for business-ready revenue (documented).
- Rejected (why): Aggregating all order statuses into Gold revenue (would mix Pending/Cancelled).

**FINAL DECISION:** Keep SQL; Prompt 19 will run them via create_gold_tables.py.

---

## Prompt 2: Gold orchestrator (playbook Prompt 19)

**PROMPT SENT:**

Implement `create_gold_tables.py` to execute/create the four Gold tables from the SQL files. CE-friendly, idempotent (createOrReplace), print row counts. Spark Connect: no rdd/JVM.

**AI RESPONSE SUMMARY:**

Orchestrator reads the four `.sql` files, `CREATE DATABASE IF NOT EXISTS gold`, runs each `CREATE OR REPLACE TABLE`, asserts Silver is non-empty via `limit(1).count()`, prints per-table counts. SQL dir from `__file__` or Workspace Users / `REPO_ROOT` fallback.

**YOUR EVALUATION:**

- Accepted (why): Idempotent; CE path fallbacks match Bronze; SQL stays source of truth.
- Changed (why): n/a
- Rejected (why): Rewriting aggregations only in PySpark (would duplicate SQL).

**FINAL DECISION:** Run on Databricks after Silver; then Prompt 20 consolidates gold logs.

