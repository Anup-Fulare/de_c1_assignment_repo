# AI Prompts — Documentation

## How to use this file

Capture Cursor exchanges for scaffolding, requirements, design, workflow docs, README, and reflection.

Append real Cursor iterations here. Do not invent prompt history after the fact.

---

## Prompt 1: Project scaffolding

**PROMPT SENT:**

Read ASSIGNMENT_PLAN.md and create the full required repository folder structure at the repo root. Create empty/skeleton files only (no full implementation). Include root markdown artifacts, tool-specific/cursor-workflow/, src/ layers with exact filenames, data/, database/, tests/, ai-prompts/, and .cursorrules (medallion layers, no secrets/PII, flag-don't-delete DQ rows, document AI decisions). Work at repo root. List every file created when done.

**AI RESPONSE SUMMARY:**

Created the required tree at repo root: skeleton markdown, Python/SQL placeholders, empty CSV placeholders, `.cursorrules`, and `ai-prompts/` files. No pipeline logic, no generated data.

**YOUR EVALUATION:**

- Accepted (why): Skeleton files match the required assignment filenames.
- Changed (why): After Prompt 1, moved the whole scaffold into `databricks-medallion-pipeline/` so the repo matches the PDF required structure (`databricks-medallion-pipeline/README.md`, `src/`, etc.). Local-only plan files stay at git repo root and remain gitignored.
- Rejected (why): n/a

**FINAL DECISION:** Use `databricks-medallion-pipeline/` as the project root for Prompts 2+.

---

## Prompt 2: Candidate info

**PROMPT SENT:**

Fill `candidate-info.md` using the assignment template with: Name Anup Devendra Fulare; Role SSE; stack Python/PySpark, SQL, Databricks; AI tool Cursor; Medallion Architecture; start date 2026-08-13; submission TBD; Databricks Free/Community Edition; libraries PySpark, Delta Lake, pandas as needed. Keep concise; Setup Summary points to README.md.

**AI RESPONSE SUMMARY:**

Wrote `databricks-medallion-pipeline/candidate-info.md` with candidate metadata, tools/environment, and a short setup summary pointing to README.md.

**YOUR EVALUATION:**

- Accepted (why): Matches the PDF candidate-info template and the details provided by the candidate.
- Changed (why): n/a
- Rejected (why): n/a

**FINAL DECISION:** Keep this candidate-info.md for the submission.

---

## Prompt 3: Requirements analysis

**PROMPT SENT:**

Using the e-commerce medallion assignment (customers, orders, products → Bronze → Silver → Gold → Dashboard), write requirements-analysis.md in with Problem Statement, Functional Requirements (per layer), Non-Functional Requirements, Assumptions, Edge Cases, and Clarifications Needed. Be specific and honest; do not pad with generic filler.

**AI RESPONSE SUMMARY:**

Wrote `databricks-medallion-pipeline/requirements-analysis.md` covering Bronze/Silver/Gold/Dashboard FRs, NFRs (CE-friendly, no real PII), assumptions, edge cases for intentional DQ issues, and a short clarifications list (DBFS path, Inactive definition, submission date TBD).

**YOUR EVALUATION:**

- Accepted (why): Tied to assignment scope; separates layers; flags-not-delete called out; honest open questions only.
- Changed (why): n/a
- Rejected (why): n/a

**FINAL DECISION:** Use this requirements-analysis.md as the baseline for design (Prompt 4).

---

## Prompt 4: Design notes + data model + DQ strategy

**PROMPT SENT:**

Create three consistent design artifacts: design-notes.md (architecture + layers + debugging), data-model.md (schemas, PK/FK, Bronze/Silver extras, Gold outputs), data-quality-strategy.md (completeness, uniqueness, type validation, RI, business logic — What/How/Threshold/Result; ~700 issue inventory; % passed report). Rules: Silver flags never deletes; four Gold aggregations including trends + High-Value/Repeat/One-Time/Inactive; document Silver→Gold filter.

**AI RESPONSE SUMMARY:**

Wrote the three docs under `databricks-medallion-pipeline/` aligned to requirements: medallion flow, exact source schemas, Silver flag columns, Gold logical tables, DQ checks with thresholds, intentional issue inventory, and Gold feed rule (pass critical checks; keep flagged rows in Silver).

**YOUR EVALUATION:**

- Accepted (why): Consistent across the three files; matches assignment schemas and flag-not-delete rule.
- Changed (why): n/a
- Rejected (why): n/a

**FINAL DECISION:** Use these design docs as the build-against spec for implementation prompts.

---

## Prompt 5: Cursor workflow pack + Part A tool-workflow

**PROMPT SENT:**

Write Cursor-specific workflow evidence and Part A: project-context.md, spec.md, cursor-rules-or-instructions.md, task-breakdown.md, and tool-workflow.md (primary tool, context, requirements/design/codegen/validation/testing/debugging/DQ, what not to share, production reuse, lessons learned as placeholders). Tone practical and honest.

**AI RESPONSE SUMMARY:**

Filled the four `tool-specific/cursor-workflow/` files and `tool-workflow.md` describing how Cursor is used on this project, condensed build spec, `.cursorrules` usage, ordered tasks 1–28 with Databricks/push checkpoints, and Part A sections with TBD lessons learned.

**YOUR EVALUATION:**

- Accepted (why): Matches assignment Part A + Cursor evidence expectations; lessons left as placeholders until after build.
- Changed (why): Corrected an initial mix-up so rules content and task-breakdown content land in the right files.
- Rejected (why): n/a

**FINAL DECISION:** Keep this workflow pack; update lessons learned after implementation.

---

## Prompt 6: Seed ai-prompts templates

**PROMPT SENT:**

Initialize each file under ai-prompts/ with official capture template headers (PROMPT SENT / RESPONSE / EVALUATION / FINAL DECISION). Add a note to append real Cursor iterations only, not invent them later. Preserve existing documentation.md history for Prompts 1–5.

**AI RESPONSE SUMMARY:**

Seeded empty templates in data-generation.md, bronze-layer.md, silver-layer.md, gold-layer.md, dashboard.md, and debugging.md. Kept documentation.md Prompt 1–5 entries; strengthened the “how to use” note about not inventing history.

**YOUR EVALUATION:**

- Accepted (why): Ready structure for layer prompt logs without wiping real documentation history.
- Changed (why): Did not replace documentation.md entries with an empty Prompt 1 template.
- Rejected (why): n/a

**FINAL DECISION:** Use these templates going forward; fill with real work from Prompt 7+.

---

## Prompt 23: Test suite

**PROMPT SENT:**

Add tests: DQ on CSVs using Silver completeness/uniqueness/RI rules; light pipeline row-count relationship checklist. Runnable without extra deps beyond pandas. Document local vs Databricks in tests/README and a short README Tests section.

**AI RESPONSE SUMMARY:**

Added `test_silver_rules_on_csv.py` (50/300/20/40/50/30 flags; nulls not orphans) and `test_pipeline_row_relationships.py` (CSV=Bronze contract + CE checklist). Updated `tests/README.md` and README Tests section. Local run: all Silver-rule assertions PASSED.

**YOUR EVALUATION:**

- Accepted (why): Proves seeded issues are detectable with the same rules as Silver; no secrets; CE still SQL-based.
- Changed (why): Spark not used locally (CE-only runtime).
- Rejected (why): n/a

**FINAL DECISION:** Keep these tests; Prompt 25 will expand full README setup.

---

## Prompt 25: End-to-end README

**PROMPT SENT:**

Write a complete README.md for this repo so a reviewer can run end-to-end on Databricks Community Edition: Prerequisites; Clone repo; Generate sample data (local command); Upload CSVs / set DBFS paths; Run Bronze → Silver → Gold (order of scripts); Create dashboard from dashboard_queries.sql; Run tests; Expected outputs / how to verify DQ report catches intentional issues; Project structure map; Responsible AI notes (no real PII). Make instructions accurate to files that actually exist. Do not claim features we did not build.

**AI RESPONSE SUMMARY:**

Replaced the skeleton README with reviewer steps tied to real files: pandas-only local deps; clone URL + `databricks-medallion-pipeline/` working dir; generate + issue-count test; Workspace-synced CSV path used on CE vs optional FileStore/`ingest_all` `data_dir` widget; Bronze (individual or ingest_all) → `create_silver_tables.py` → `create_gold_tables.py`; dashboard SQL + guide + sample results + screenshots (no dashboard JSON/job); local Python tests vs CE SQL counts; seeded issue table including uniqueness flag doubling; structure map; synthetic PII / no secrets.

**YOUR EVALUATION:**

- Accepted (why): Matches scripts, CE Spark Connect notes, and files that exist; does not claim pytest as a required dependency, Unity Catalog, or exported dashboards.
- Changed (why): Documented two CSV locations (Workspace repo vs FileStore) because ingest_all defaults differ from the CE-tested individual ingest path.
- Rejected (why): n/a

**FINAL DECISION:** Use this README as the end-to-end runbook for reviewers.

---

## Prompt 26: Reflection + final AI usage summary

**PROMPT SENT:**

Draft reflection.md and final-ai-usage-summary.md based on my real experience. Use these notes:

What I built: E-commerce medallion on Databricks Community Edition: synthetic CSVs (~10k customers, 100k orders, 500 products) with seeded DQ issues; Bronze raw Delta ingest; Silver flag-only quality (completeness, uniqueness, types, RI, business rules) plus silver.quality_metrics; four Gold tables; Gold-only dashboard SQL. Cursor for codegen/docs; I ran Bronze/Silver/Gold/dashboard SQL on CE.

Where AI helped most: Scaffolding and keeping design/DQ docs aligned; first-pass PySpark/SQL for each layer; turning the assignment issue inventory into generator + tests; README/runbook after the pipeline existed. Faster than writing every flag column and Gold CTE from scratch.

What AI got wrong: Bronze assumed classic Spark (rdd.isEmpty(), _jvm, dbutils.fs.ls) and /FileStore/... — CE is Spark Connect and Workspace /Workspace/Users/{user}/... paths. Generator wrote integer IDs as floats (5764.0) so Spark IntegerType nulled almost all FKs. Local pandas tests still passed. AI also mixed FileStore vs Workspace defaults (ingest_all vs per-file ingest).

How I validated AI output: Compared code to data-model.md / DQ strategy; ran test_sample_data_issues.py and Silver-rule CSV tests locally; after each CE run checked Bronze counts (10010 / 100000 / 500), Silver = Bronze, quality_metrics vs seeded 50/100/200/50/30/20 (and uniqueness 20/40 flagged rows); Gold row shapes and dashboard Q1 = 10 rows. Logged accept/change/reject in ai-prompts/. Did not treat “looks like Databricks” as enough.

What I’d improve next: Pin CE constraints in .cursorrules before first ingest (no rdd/_jvm). Spot-check CSV ID strings and Spark null counts before Silver. One documented CSV path. Keep CE stack traces in debugging-notes.md when they happen, not only git diffs. Optional: notebook that runs Bronze→Silver→Gold in order.

Reusable workflow for production: Write a short spec + in-repo rules first; generate one layer at a time; human-review DQ (flag vs drop, Gold filters); test on the same runtime as prod/CE; never paste secrets; keep prompt logs for audit. Treat AI as a first draft, not the source of truth for joins or quality semantics.

Be honest and specific. Avoid generic praise of AI. Update tool-workflow.md lessons-learned section with the same truths.

**AI RESPONSE SUMMARY:**

Filled `reflection.md` (six sections from the notes, first person, CE bugs named). Filled `final-ai-usage-summary.md` (tool, layer table, failures with commits, validation, production reuse). Replaced TBD lessons in `tool-workflow.md` with the same truths.

**YOUR EVALUATION:**

- Accepted (why): Matches candidate notes and debugging-notes.md; no generic AI praise; no invented extra bugs.
- Changed (why): n/a
- Rejected (why): n/a

**FINAL DECISION:** Keep these three files as the reflection close-out; Prompt 27 will reuse them for form answers.

---

## Prompt 27: Form answer draft (submission)

**PROMPT SENT:**

Draft short written answers I can paste into the submission form: (1) My understanding of the medallion architecture problem (2) How I used AI across data generation, ingestion, validation, aggregation (3) Key design/implementation decisions made with AI (4) Testing and validation approach (5) How I validated AI output (6) What I’d improve next. Keep answers in my voice, concrete, and aligned with reflection.md / ai-prompts/.

**AI RESPONSE SUMMARY:**

Wrote `submission-form-answers.md` with six paste-ready answers: medallion layers + flag-not-delete + Gold filters; Cursor by phase with CE as the human gate; CE Spark Connect + Int64 IDs + metrics; local tests + CE counts; AI validation including the two real failures; next-time rules/path/traces.

**YOUR EVALUATION:**

- Accepted (why): Matches reflection and debugging-notes; short enough to paste; no generic AI praise.
- Changed (why): Output file is `submission-form-answers.md` because the prompt did not name a path; it is a paste aid, not a new pipeline feature.
- Rejected (why): n/a

**FINAL DECISION:** Use these six answers for the form; edit if the portal has a character cap.

---

## Prompt 28: Completeness audit vs plan

**PROMPT SENT:**

Audit the repository against ASSIGNMENT_PLAN.md acceptance criteria and the required file tree. For each required file/folder: exists? non-empty? purpose met? For each acceptance checkbox: pass/fail + evidence path. List gaps only — then propose the smallest fixes to close them (do not expand scope).

**AI RESPONSE SUMMARY:**

Audited `ASSIGNMENT_PLAN.md` against `databricks-medallion-pipeline/`. Required tree present and non-empty. Core acceptance: pass (CSVs, Bronze/Silver/Gold/dashboard, tests, README, prompt logs, reflection). Nested folder vs plan “repo root” is an accepted PDF-structure deviation (Prompt 1). One doc gap: strategy lacked CE detection results — added observed proof table to `data-quality-strategy.md` without inventing `pct_passed`. `.cursorrules` no longer references the gitignored plan file.

**YOUR EVALUATION:**

- Accepted (why): Honest pass/fail; no scope expansion (no flatten, no fake metrics).
- Changed (why): Smallest doc fixes only (strategy results + rules path).
- Rejected (why): Flattening to git root; fabricating CE % passed; extra audit markdown file.

**FINAL DECISION:** Treat assignment artifacts as complete aside from out-of-repo steps (submit form + GitHub link).


