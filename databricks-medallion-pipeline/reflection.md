# Reflection

Honest notes from building this assignment with Cursor on Databricks Free/Community Edition. Not a sales pitch for AI.

## What I built

An e-commerce **medallion** pipeline: synthetic CSVs (~10k customers, 100k orders, 500 products) with **seeded** data-quality issues; **Bronze** raw Delta ingest (no cleaning); **Silver** flag-only checks (completeness, uniqueness, type validation, referential integrity, business logic) plus `silver.quality_metrics`; **four Gold** aggregations; **Gold-only** dashboard SQL.

I used Cursor for codegen and docs. I ran Bronze, Silver, Gold, and dashboard SQL on Community Edition myself.

## Where AI helped most

- Scaffolding the folder tree and keeping requirements / design / data model / DQ strategy aligned
- First-pass PySpark and Spark SQL for each layer
- Turning the assignment issue inventory into `generate_sample_data.py` and local tests
- Expanding the README after the pipeline actually existed

That was faster than hand-writing every `flag_*` column and Gold CTE from a blank file.

## What AI got wrong

- Bronze assumed **classic Spark**: `rdd.isEmpty()`, `_jvm`, `dbutils.fs.ls`, and hardcoded `/FileStore/...`. CE compute is **Spark Connect**. Workspace CSVs lived under `/Workspace/Users/{user}/...`, not only FileStore.
- The generator wrote integer IDs as floats (`5764.0`) because of pandas `NA`. Spark `IntegerType` then nulled almost all FKs. Local pandas tests still passed.
- Path defaults drifted: `ingest_all.py` still leans FileStore; per-file ingest auto-detects the Workspace repo path.

These are in `debugging-notes.md` (commits `303de8b`, `afe62eb`).

## How I validated AI output

- Compared generated code to `data-model.md` and `data-quality-strategy.md`
- Ran `tests/test_sample_data_issues.py` and Silver-rule CSV tests locally
- On CE: Bronze counts **10010 / 100000 / 500**; Silver row counts equal Bronze; `silver.quality_metrics` vs seeded **50 / 100 / 200 / 50 / 30 / 20** (uniqueness flags **20 / 40** rows because every duplicate id is flagged)
- Gold table shapes; dashboard Q1 returns **10** rows
- Logged accept / change / reject in `ai-prompts/`

“Looks like Databricks” was not enough. The float-ID bug proved local CSV tests can pass while Spark ingest fails.

## What I would improve next

- Put CE constraints in `.cursorrules` **before** first ingest (no `rdd` / `_jvm`)
- Spot-check CSV ID strings and Spark null-FK counts **before** Silver
- One documented CSV path, not FileStore vs Workspace split
- Paste CE stack traces into `debugging-notes.md` when they happen, not only git diffs later

## Reusable workflow for production

Write a short spec and in-repo rules first. Generate **one layer at a time**. A human reviews DQ semantics (flag vs drop, Gold filters). Test on the **same** runtime as the target (here: CE / Spark Connect). Never paste secrets. Keep prompt logs for audit. Treat AI as a **first draft**, not the source of truth for joins or quality rules.
