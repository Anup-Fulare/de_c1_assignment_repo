# AI Prompts — Dashboard

## How to use this file

Append real Cursor iterations for dashboard SQL and Databricks SQL Dashboard setup guide. Do not invent prompt history after the fact.

---

## Prompt 1: Dashboard queries + guide (playbook Prompt 21)

**PROMPT SENT:**

Create `dashboard_queries.sql` (top 10 products bar, customer revenue histogram bins, segmentation pie; optional filters as comments) and `DASHBOARD_GUIDE.md` for Databricks SQL Dashboard on Community Edition. Queries read Gold only.

**AI RESPONSE SUMMARY:**

Four Gold-only queries (3 required + daily trend extra). Guide: SQL Editor → saved queries → dashboard tiles (bar/pie/line), CE fallback via notebook charts, no secrets, sanity checks vs Gold counts.

**YOUR EVALUATION:**

- Accepted (why): Matches assignment viz types; Gold-only; CE limitations documented.
- Changed (why): n/a
- Rejected (why): Reading Silver/Bronze in dashboard queries.

**FINAL DECISION:** Use these queries on CE after Gold; Prompt 22 consolidates this log.

---

## Prompt 2: Consolidate Prompt 21 log (playbook Prompt 22)

**PROMPT SENT:**

Append Prompt 21 into `ai-prompts/dashboard.md`. Notes: Gold already OK on CE; dashboard SQL is Gold-only (top 10, bins, pie, optional daily). Sample result notes / screenshots may live under `src/dashboard/`.

**AI RESPONSE SUMMARY:**

Prompt 21 entry already complete. Added this consolidation. Dashboard queries do not change Bronze/Silver/Gold tables.

**YOUR EVALUATION:**

- Accepted (why): Three required viz queries + guide; extra daily query is optional.
- Changed (why): n/a
- Rejected (why): n/a

**FINAL DECISION:** Phase 5 prompt log complete. Next: test suite (Prompt 23).

