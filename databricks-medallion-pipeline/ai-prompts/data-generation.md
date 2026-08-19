# AI Prompts — Data Generation

## How to use this file

Append real Cursor iterations for sample data generation, verification, and database seed/setup notes. Do not invent prompt history after the fact.

---

## Prompt 1: Generator design + script (playbook Prompt 7)

**PROMPT SENT:**

Implement `src/data_generation/generate_sample_data.py` to create realistic e-commerce CSVs at `data/customers.csv`, `data/orders.csv`, `data/products.csv` with volumes 10k/100k/500, exact intentional DQ issues, pandas+stdlib, seed, verification summary, and `DATA_GENERATION_NOTES.md`.

**AI RESPONSE SUMMARY:**

Implemented generator with seed 42; wrote products (500), customers (10,000 + 10 dup rows), orders (100,000) with disjoint intentional issues; added notes and pinned `pandas` in `requirements.txt`. Ran script; verification counts matched assignment expectations.

**YOUR EVALUATION:**

- Accepted (why): Exact intentional counts verified on run (50 null emails, 10 dup customer rows, 100/200 nulls, 50/30 orphans, 20 dup order rows).
- Changed (why): Avoided Faker; used stdlib name lists. Fixed duplicate `to_csv` calls before final write.
- Rejected (why): n/a

**FINAL DECISION:** Keep this generator; harden with formal asserts in Prompt 8.

---

## Prompt 2: Verify issue counts (playbook Prompt 8)

**PROMPT SENT:**

Add a verification helper/tests that assert intentional DQ issue counts on generated CSVs match the assignment exactly; run until all assertions pass; report actual counts.

**AI RESPONSE SUMMARY:**

Added `tests/test_sample_data_issues.py` (runnable via `python tests/test_sample_data_issues.py` or pytest). Asserts null emails, duplicate extras, null FKs, orphans, duplicate orders, and row volumes. Run result: all assertions PASSED with expected counts.

**YOUR EVALUATION:**

- Accepted (why): Formal asserts match assignment inventory; no generator fixes needed.
- Changed (why): n/a
- Rejected (why): n/a

**FINAL DECISION:** Keep the test as the regression check after regenerating CSVs.

---

## Prompt 3: Database schema + seed notes (playbook Prompt 9)

**PROMPT SENT:**

Create `database/schema.sql` (Bronze/Silver/Gold Delta-friendly), `seed-data-notes.md`, and `setup-notes.md` for Databricks Community Edition DBFS upload and CSV→table mapping. Keep secrets out.

**AI RESPONSE SUMMARY:**

Wrote DDL for bronze/silver/gold tables (including Silver flags + quality_metrics and four Gold tables), seed mapping notes, and CE setup steps with suggested `/FileStore/medallion_pipeline/data` paths and no credentials in-repo.

**YOUR EVALUATION:**

- Accepted (why): Aligns with data-model.md; CE-friendly; clear upload/run order.
- Changed (why): n/a
- Rejected (why): n/a

**FINAL DECISION:** Use these database docs; ingest scripts will reference the same DBFS base path.

---

## Prompt 4: Consolidate Prompt 7–9 log (playbook Prompt 10)

**PROMPT SENT:**

Append real Prompt 7–9 exchanges into `ai-prompts/data-generation.md` using the evaluation template. Extra notes paste: none (already logged after each run).

**AI RESPONSE SUMMARY:**

Confirmed Prompts 7–9 already have full entries in this file (generator, asserts PASSED, schema/setup notes). Added this consolidation entry; no invented history.

**YOUR EVALUATION:**

- Accepted (why): History already complete and truthful; consolidation documents Prompt 10 without duplicating large blocks.
- Changed (why): n/a
- Rejected (why): n/a

**FINAL DECISION:** Phase 1 prompt history complete; proceed to Bronze (Prompt 11).
