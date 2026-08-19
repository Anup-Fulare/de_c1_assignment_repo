# Task breakdown for Cursor

Ordered tasks aligned to `ASSIGNMENT_PLAN.md` / `ASSIGNMENT_PROMPTS.md`. Confirm before each run; log after.

## Phase 0 — Foundation

1. Scaffold required tree under `databricks-medallion-pipeline/`
2. Fill `candidate-info.md`
3. Write `requirements-analysis.md`
4. Write `design-notes.md`, `data-model.md`, `data-quality-strategy.md`
5. Write Cursor workflow pack + Part A `tool-workflow.md`
6. Seed `ai-prompts/` templates (keep existing real entries)

## Phase 1 — Data

7. Implement `generate_sample_data.py` + notes; write CSVs with exact intentional issues
8. Assert intentional issue counts (tests/helper)
9. `database/schema.sql` + seed/setup notes
10. Log data-generation prompts into `ai-prompts/data-generation.md`

## Phase 2 — Bronze

11. Individual Bronze ingest scripts (customers, orders, products)
12. `ingest_all.py` orchestrator
13. Log bronze prompts

## Phase 3 — Silver

14. Completeness + uniqueness modules
15. Type validation, referential integrity, business logic
16. `create_silver_tables.py` + quality metrics report
17. Log silver prompts

## Phase 4 — Gold

18. Four Gold SQL aggregations
19. `create_gold_tables.py`
20. Log gold prompts

## Phase 5 — Dashboard

21. `dashboard_queries.sql` + `DASHBOARD_GUIDE.md`
22. Log dashboard prompts

## Phase 6 — Hardening

23. Test suite (DQ + light pipeline)
24. `debugging-notes.md` from real issues
25. End-to-end `README.md`

## Phase 7 — Close-out

26. `reflection.md` + `final-ai-usage-summary.md` (+ lessons in tool-workflow)
27. Submission form answer draft
28. Completeness audit vs plan

## Push / Databricks checkpoints (reminder)

- Optional commit after docs (1–6)
- Push after data gen verified (7–9) — still local
- First Databricks CE test after Bronze code (11–12)
- Re-test after Silver 16 and Gold 19; dashboard after 21
- Final push / PR after audit 28
