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
