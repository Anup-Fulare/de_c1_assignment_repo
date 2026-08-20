# Final AI Usage Summary

**Tool:** Cursor (Agent for multi-file work; Ask for explanations)  
**Candidate:** Anup Devendra Fulare  
**Environment:** Databricks Free/Community Edition + local Python/pandas

## How Cursor was used

| Area | Role of AI | Human gate |
|------|------------|------------|
| Requirements / design | Draft `requirements-analysis.md`, `design-notes.md`, `data-model.md`, `data-quality-strategy.md` | Edit until flag-don’t-delete and layer boundaries match the assignment |
| Data generation | `generate_sample_data.py` + seeded issue counts | Local assert tests; later CE null-FK check |
| Bronze | Ingest scripts + `ingest_all.py` | CE run; Spark Connect rewrite after failure |
| Silver | Quality modules 01–05 + `create_silver_tables.py` + metrics | CE run; Silver count = Bronze; metrics vs inventory |
| Gold | Four `.sql` files + `create_gold_tables.py` | CE run; Completed-only / critical-flag filters |
| Dashboard | `dashboard_queries.sql` + guide | Run Gold SQL on CE (Q1 = 10 rows) |
| Tests / README / debug | Local tests, README, `debugging-notes.md` | Only real CE issues documented |

Prompt history: `ai-prompts/` (not invented after the fact). Standing rules: `.cursorrules`. Workflow: `tool-workflow.md`.

## Where AI helped

Scaffolding and keeping design docs consistent; first-pass PySpark/SQL; mapping the ~700-row issue inventory into a generator and tests; README after code existed.

## Where AI failed (and what we did)

1. **Classic Spark APIs on Spark Connect** — dropped `rdd` / `_jvm` / `dbutils.fs` path checks; Workspace user path + widgets (`303de8b`).
2. **Float IDs in CSV** — pandas `Int64` before `to_csv`; regenerated CSVs (`afe62eb`).
3. **Two default data paths** — documented in README; did not pretend they were the same.

## Validation of AI output

Local: `test_sample_data_issues.py`, `test_silver_rules_on_csv.py`, `test_pipeline_row_relationships.py`.  
CE: Bronze volumes, Silver = Bronze, quality_metrics vs seeded issues, Gold + dashboard SQL.  
Decisions recorded as Accepted / Changed / Rejected under `ai-prompts/`.

## What I would not reuse blindly

Generated ingest that “looks like Databricks” without running on the submission cluster. Generated DQ SQL without checking Gold filters against Silver flags. Any prompt that needs secrets — none went into this repo.

## Production reuse (short)

Spec + rules in-repo → phased prompts → same-runtime test → human review of DQ and joins → prompt log → no credentials in chat or git.
