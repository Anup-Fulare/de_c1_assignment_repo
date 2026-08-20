# AI Prompts — Bronze Layer

## How to use this file

Append real Cursor iterations for Bronze ingest scripts and orchestration. Do not invent prompt history after the fact.

---

## Prompt 1: Individual Bronze ingest scripts (playbook Prompt 11)

**PROMPT SENT:**

Implement Bronze ingestion for Databricks (PySpark) with NO transformations/cleaning for customers, orders, products: configurable DBFS path, schema/casts, bronze.* Delta tables, ingest metadata, input validation, CE-friendly. Do not clean bad rows.

**AI RESPONSE SUMMARY:**

Implemented `01_ingest_customers.py`, `02_ingest_orders.py`, `03_ingest_products.py` with explicit schemas, date casts only, `_ingest_source_path` / `_ingest_ts`, `saveAsTable` overwrite to `bronze.*`, optional Databricks widgets defaulting to `/FileStore/medallion_pipeline/data/...`.

**YOUR EVALUATION:**

- Accepted (why): Raw ingest only; preserves intentional DQ issues; matches design-notes naming.
- Changed (why): n/a
- Rejected (why): n/a

**FINAL DECISION:** Keep these scripts; wire via `ingest_all.py` in Prompt 12.

---

## Prompt 2: Bronze orchestrator (playbook Prompt 12)

**PROMPT SENT:**

Implement `src/bronze/ingest_all.py` to run all three Bronze ingestions in sequence, fail fast on error, and print a combined metadata summary (per-table row counts + timestamps). Align with design-notes.md naming.

**AI RESPONSE SUMMARY:**

Added `ingest_all.py` calling `ingest_customers` → `ingest_orders` → `ingest_products` against `bronze.*` tables, default data dir `/FileStore/medallion_pipeline/data`, optional `data_dir` widget, fail-fast with printed combined summary.

**YOUR EVALUATION:**

- Accepted (why): Fail-fast sequence and metadata summary match the playbook; table names match design-notes.
- Changed (why): n/a
- Rejected (why): n/a

**FINAL DECISION:** Keep ingest_all.py as the Bronze entrypoint.

---

## Prompt 3: Consolidate Prompt 11–12 log (playbook Prompt 13)

**PROMPT SENT:**

Append Prompt 11–12 results into `ai-prompts/bronze-layer.md` with accept/change/reject notes. Extra notes: latest pull updated Bronze files for Databricks Free/Community Edition (Spark Connect) compatibility; future prompts should follow those patterns.

**AI RESPONSE SUMMARY:**

Prompts 11–12 already had full entries. Added this consolidation. Recorded CE compatibility from the pulled code as the reference for later layers: no JVM/`dbutils.fs` path checks; `df.limit(1).count()` instead of `rdd.isEmpty()`; auto-detect Workspace user path (`/Workspace/Users/{user}/.../databricks-medallion-pipeline/data`); widgets as optional override.

**YOUR EVALUATION:**

- Accepted (why): Bronze history is complete; pulled CE patterns are the compatibility baseline going forward.
- Changed (why): After Databricks testing, ingest scripts dropped Spark Connect-incompatible validation (`dbutils`/`rdd`); kept raw ingest and `bronze.*` table names.
- Rejected (why): n/a

**FINAL DECISION:** Phase 2 prompt history complete. Implement Silver (Prompt 14+) using the pulled Bronze style as the CE reference.

