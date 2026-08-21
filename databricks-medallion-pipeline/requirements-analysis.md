# Requirement Analysis

## Problem Statement

An e-commerce company needs a Databricks medallion pipeline for daily sales data from three sources: customers, orders, and products. Raw CSVs must land in Bronze unchanged, be quality-checked and flagged (not silently deleted) in Silver, aggregated into business-ready Gold tables, and exposed through a Databricks SQL dashboard for stakeholders. The work also demonstrates an AI-assisted data engineering workflow (Cursor), with visible thinking across requirements, design, implementation, testing, debugging, and reflection.

## Functional Requirements

### Bronze
- Ingest `customers.csv`, `orders.csv`, and `products.csv` from DBFS/S3-style paths into Bronze Delta tables
- Preserve raw data: no cleaning, no dropping rows, no business transforms
- Apply schema inference / explicit types for storage as raw Bronze
- Log ingestion metadata (source path, row counts, timestamp)
- Validate inputs (path exists / non-empty) with clear errors

### Silver
- Implement data quality checks: completeness, uniqueness, type validation, referential integrity, and business logic
- Flag bad rows (e.g. `quality_check_result` and/or per-check flags); never silently delete
- Produce a quality metrics report showing % passed per check
- Detect the intentional seeded issues in sample data (~700 problematic rows)

### Gold
- Build four aggregation tables:
  - Sales by product (orders, revenue, AOV)
  - Revenue by customer (orders, revenue, AOV, lifetime_value_actual)
  - Daily / weekly trends
  - Customer segmentation (High-Value / Repeat / One-Time / Inactive)
- Document which Silver rows feed Gold (analytics on rows that pass critical checks; flagged rows retained in Silver)

### Dashboard
- Provide 3+ Databricks SQL queries/visualizations from Gold only:
  - Top 10 products by revenue (bar)
  - Customer revenue distribution (histogram-friendly)
  - Customer segmentation (pie)
- Document how to wire tiles on Free/Community Edition

### Supporting deliverables
- Sample data generator with exact intentional DQ issues
- Database schema / setup notes
- README with end-to-end setup
- At least one meaningful test tier (DQ / light pipeline)
- AI prompt history and lifecycle artifacts (requirements, design, reflection, etc.)

## Non-Functional Requirements

- Maintainable, readable, commented Python / PySpark / SQL
- Reproducible sample data (fixed RNG seed)
- Databricks Free/Community Edition–friendly paths and simple setup
- No real customer PII, secrets, or production credentials
- Clear separation of medallion layer responsibilities
- Prompt history and design docs accurate to real work (not invented after the fact)

## Assumptions

- Development/testing uses Databricks Free/Community Edition
- CSVs are generated locally and uploaded to DBFS (or equivalent) for ingest
- Bronze/Silver/Gold persist as Delta tables (or CE-equivalent table storage)
- Products catalog is the clean reference for referential checks; intentional orphans only appear in orders
- Gold analytics exclude rows that fail critical Silver checks, while Silver keeps all rows with flags
- Primary AI tool is Cursor; local plan/playbook files stay gitignored at repo root

## Edge Cases

- NULL `email`, `customer_id`, or `product_id` (completeness)
- Duplicate `customer_id` / `order_id` (uniqueness)
- Orphan FKs: `customer_id` / `product_id` not in parent tables
- Cancelled / Pending orders and nullable `payment_date`
- Amount mismatches (`total_amount` vs `quantity * unit_price`)
- Invalid or future dates, invalid `order_status` / `customer_segment` values
- Empty or missing source files at ingest time

## Clarifications resolved

- **CSV / DBFS path:** On Free/Community Edition, Bronze ingest reads CSVs from the Workspace repo `.../databricks-medallion-pipeline/data/` (see README). Optional FileStore path: `/FileStore/medallion_pipeline/data` via `ingest_all` `data_dir` or per-file `source_path` widgets.
- **Inactive:** Gold treats Inactive as **0 completed orders** in this dataset, including cancelled-only and never-completed customers (`src/gold/04_customer_segmentation.sql`).
- **Submission date:** **2026-08-21** (`candidate-info.md`).
