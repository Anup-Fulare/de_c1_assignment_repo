# Submission form answers (paste-ready)

Short drafts aligned with `reflection.md`, `final-ai-usage-summary.md`, and `ai-prompts/`. Edit tone if the form has a character limit.

---

## 1) My understanding of the medallion architecture problem

The problem is to take messy e-commerce CSVs (customers, orders, products) and produce trustworthy KPIs without hiding bad data. **Bronze** is a raw, auditable copy (Delta, no cleaning). **Silver** applies completeness, uniqueness, type, referential-integrity, and business-logic checks by **flagging** rows, never deleting them, and writes a % passed report (`silver.quality_metrics`). **Gold** aggregates only rows that pass the critical flags (and Completed orders for revenue) into sales-by-product, revenue-by-customer, trends, and High-Value / Repeat / One-Time / Inactive segments. A dashboard reads **Gold only**. Intentional defects in the sample (~700 issue instances) exist so Silver can prove it catches them.

---

## 2) How I used AI across data generation, ingestion, validation, aggregation

I used **Cursor** with a written spec (`.cursorrules`, design/DQ docs) and phase-scoped prompts. AI drafted the pandas generator with exact seeded issue counts, Bronze ingest, Silver flag modules + orchestrator, Gold SQL + `create_gold_tables.py`, and dashboard queries. I generated CSVs locally, ran pandas tests, then executed Bronze → Silver → Gold → dashboard SQL myself on Databricks Community Edition. Prompt decisions are in `ai-prompts/` (accepted / changed / rejected). I did not paste secrets or real PII into the tool.

---

## 3) Key design/implementation decisions made with AI

- **Flag, don’t delete** in Silver; Gold filters critical flags (`completeness`, `uniqueness`, `referential_integrity`) and Completed status for revenue.
- **CE / Spark Connect:** no `rdd` / `_jvm` / `dbutils.fs` path listing; empty check via `limit(1).count()`; Workspace user path for CSVs after classic Spark ingest failed.
- **Pandas `Int64`** before `to_csv` so IDs are not written as `5764.0` (that nulled Spark `IntegerType` FKs).
- Separate quality modules 01–05 plus `silver.quality_metrics` and console proof vs the seeded inventory.
- Dashboard SQL over Gold only; notebook charts if SQL Dashboards are limited on CE.

---

## 4) Testing and validation approach

**Local:** `test_sample_data_issues.py` (seeded counts), `test_silver_rules_on_csv.py` (same completeness/uniqueness/RI rules as Silver), `test_pipeline_row_relationships.py` (CSV volumes = Bronze contract).

**Databricks CE:** Bronze row counts 10010 / 100000 / 500; Silver counts equal Bronze; `silver.quality_metrics` vs 50 null emails, 100/200 null FKs, 50/30 orphans, 20 duplicate order ids (uniqueness flags 20 customer / 40 order rows); Gold table shapes; dashboard Q1 returns 10 rows. Failures that were real are in `debugging-notes.md`.

---

## 5) How I validated AI output

I compared generated code to `data-model.md` and `data-quality-strategy.md`, ran the local tests above, and re-checked counts on CE after each layer. I did not accept “looks like Databricks”: first ingest used classic Spark APIs that CE does not support, and local pandas tests passed while Spark still nulled FKs. I logged accept/change/reject in `ai-prompts/` and only documented bugs we actually hit.

---

## 6) What I’d improve next

Put Spark Connect constraints in `.cursorrules` **before** the first ingest. Spot-check CSV ID strings and Spark null-FK counts before Silver. Use one documented CSV path (FileStore vs Workspace split was confusing). Save CE stack traces in `debugging-notes.md` when they happen, not only git diffs later. Optionally add one notebook that runs Bronze → Silver → Gold in order.
