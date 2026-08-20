# AI Prompts — Silver Layer

## How to use this file

Append real Cursor iterations for Silver quality checks, orchestration, and metrics reports. Do not invent prompt history after the fact.

---

## Prompt 1: Completeness + uniqueness (playbook Prompt 14)

**PROMPT SENT:**

Implement Silver quality modules for Databricks/PySpark: `01_quality_completeness.py` (NULL email / customer_id / product_id) and `02_quality_uniqueness.py` (duplicate customer_id / order_id). Flag only, never delete. Return results reusable by `create_silver_tables.py` and % passed metrics per data-quality-strategy.md. Follow pulled Bronze Spark Connect CE patterns.

**AI RESPONSE SUMMARY:**

Implemented DataFrame helpers `flag_*_completeness` / `flag_*_uniqueness` plus `run_*` entrypoints that read Bronze tables. Completeness flags null email or null order FKs. Uniqueness uses a window count and flags every row in a duplicate key group. Metrics include total/failed/pct_passed and threshold_met. No rows dropped. Spark Connect: `limit(1).count()`, no rdd/JVM.

**YOUR EVALUATION:**

- Accepted (why): Matches DQ strategy (flag, don’t delete; metrics shape); CE-safe like pulled Bronze.
- Changed (why): Modules do not persist Silver yet — orchestration is Prompt 16.
- Rejected (why): n/a

**FINAL DECISION:** Keep these modules; Prompt 15 adds type/RI/business checks; Prompt 16 writes Silver tables.

---

## Prompt 2: Type, RI, business logic (playbook Prompt 15)

**PROMPT SENT:**

Implement `03_quality_type_validation.py`, `04_quality_referential_integrity.py`, `05_quality_business_logic.py`. Flag only; never drop. Align with data-quality-strategy.md. Spark Connect CE style like pulled Bronze.

**AI RESPONSE SUMMARY:**

Type: email regex when present, allowed segment/status, non-negative amounts, required dates. RI: left-join to distinct parent keys; NULL FKs not treated as orphans. Business: amount vs qty*price (0.01), Completed requires payment_date, signup_date not > current_date+1. Metrics + DataFrame helpers for Prompt 16. No deletes.

**YOUR EVALUATION:**

- Accepted (why): Rules match strategy; CE-safe joins/counts; reusable flag_* helpers.
- Changed (why): n/a
- Rejected (why): n/a

**FINAL DECISION:** Keep these three modules; Prompt 16 orchestrates and writes Silver + quality report.

---

## Prompt 3: Silver orchestration + quality report (playbook Prompt 16)

**PROMPT SENT:**

Implement `create_silver_tables.py`: read Bronze, apply checks 01–05, write Silver with `quality_check_result` and flag columns, quality metrics report, prove intentional seeded issues detected. Update data-quality-strategy.md report section. CE/Spark Connect compatible.

**AI RESPONSE SUMMARY:**

Orchestrator chains all flag_* helpers, sets PASS/FAIL + failure reasons, writes `silver.customers/orders/products` and `silver.quality_metrics`, prints detection proof vs expected inventory. Updated DQ strategy with report table shape and example SQL.

**YOUR EVALUATION:**

- Accepted (why): Flag-only Silver persist; metrics table; proof block matches assignment inventory.
- Changed (why): Uses importlib for numbered modules like Bronze `ingest_all.py`.
- Rejected (why): n/a

**FINAL DECISION:** Run on Databricks after Bronze; then Prompt 17 consolidates silver prompt logs.


