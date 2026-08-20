# AI Prompts — Debugging

## How to use this file

Append real Cursor iterations and CE test-and-pull cycles. Do not invent prompt history after the fact.

This file documents **git-recorded** Databricks Free/Community Edition fixes (pulls after failed/wrong runs). Exact stack traces were not committed; details follow commit messages and diffs.

---

## Prompt 1: Bronze Spark Connect compatibility (git `303de8b`)

**PROMPT SENT:**

(On Databricks CE after Prompt 11/12 ingest.) Original Bronze used `df.rdd.isEmpty()`, `spark._jvm` / Hadoop FS, and `dbutils.fs.ls`, plus hardcoded `/FileStore/medallion_pipeline/data`. Runtime did not support those APIs. Fix ingest for Spark Connect / serverless and portable Workspace user paths; keep raw ingest (no cleaning).

**AI RESPONSE SUMMARY:**

Pull `303de8b` (“Make bronze ingestion Spark Connect-compatible and parameterized”):

- Removed RDD empty-check → `limit(1).count() == 0`
- Removed JVM / `dbutils.fs` path validation; load fails if missing
- Auto-detect `/Workspace/Users/{user}/ttn_de_c1_assignment_repo_sync/databricks-medallion-pipeline/data/...`
- `REPO_ROOT` fallback; widget override kept

Same pattern applied to customers, orders, and products ingest scripts.

**YOUR EVALUATION:**

- Accepted (why): Matches CE/Spark Connect; Bronze still flag-free raw ingest into `bronze.*`.
- Changed (why): Default CSV location moved from `/FileStore/...` to synced Workspace repo path used in CE.
- Rejected (why): Keeping `rdd` / `_jvm` “because classic Databricks examples use them.”

**FINAL DECISION:** Use pulled Bronze as the CE compatibility reference for Silver/Gold.

---

## Prompt 2: Integer IDs as floats in CSV (git `afe62eb`)

**PROMPT SENT:**

After Bronze on CE, nearly all order `customer_id` / `product_id` values were NULL (not the seeded 100/200). Investigate CSV + Spark IntegerType. Fix generator so IDs stay integers when pandas NA is used.

**AI RESPONSE SUMMARY:**

Pull `afe62eb` (“Fix data generation to prevent float conversion of integer IDs”):

- Root cause: pandas float64 + `pd.NA` → CSV `'5764.0'` → Spark `IntegerType()` nulls
- Fix: `.astype("Int64")` on integer columns; regenerate `data/orders.csv`

**YOUR EVALUATION:**

- Accepted (why): Explains mass-null FKs; restores intentional DQ counts for Silver.
- Changed (why): Regenerated seed CSVs; local generator must stay Int64 going forward.
- Rejected (why): “Fix it only in Spark with a double-then-int cast” as the only fix — source CSV should be correct.

**FINAL DECISION:** Keep Int64 generation; re-verify null FK counts on CE after every CSV regenerate.

---

## Later issues

**Playbook Prompt 24:** No further pipeline bugs after Issues 1–2. Silver, Gold, and dashboard SQL succeeded on Databricks CE. No extra entries invented.

