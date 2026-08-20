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
