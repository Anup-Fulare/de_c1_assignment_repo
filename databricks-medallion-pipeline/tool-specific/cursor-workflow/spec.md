# Build specification (Cursor)

Condensed spec Cursor (and humans) should follow. Detail lives in design docs.

## Goal

E-commerce medallion pipeline on Databricks Free/Community Edition:  
**CSV → Bronze (raw) → Silver (flag DQ) → Gold (4 aggs) → SQL Dashboard (3+ tiles)**

## Project root

`databricks-medallion-pipeline/` (assignment deliverables)

## Schemas (summary)

- **customers** (~10k): customer_id PK, name, email, country, signup_date, segment (Premium/Standard/Basic), lifetime_value
- **orders** (~100k): order_id PK, customer_id FK, order_date, product_id FK, quantity, unit_price, total_amount, order_status, payment_date nullable
- **products** (~500): product_id PK, name, category, price, cost, stock_quantity, reorder_level

## Intentional DQ issues (exact)

Customers: 50 NULL email; 10 duplicate customer_id  
Orders: 100 NULL customer_id; 200 NULL product_id; 50 orphan customers; 30 orphan products; 20 duplicate order_id  
Products: clean

## Layer rules

| Layer | Must | Must not |
|-------|------|----------|
| Bronze | Ingest raw + metadata log | Clean / drop / business transforms |
| Silver | Flag bad rows + % passed report | Silently delete rows |
| Gold | 4 aggregations from filtered Silver | Read raw CSV directly |
| Dashboard | 3+ queries from Gold | Bypass Gold |

## Gold outputs

1. sales_by_product  
2. revenue_by_customer  
3. daily_weekly_trends  
4. customer_segmentation (High-Value / Repeat / One-Time / Inactive)

## Acceptance (core)

- CSVs + intentional issues verified  
- Bronze ingest ×3  
- Silver checks working + report  
- Gold calcs correct  
- Dashboard 3+ tiles documented  
- Tests catch seeded issues  
- README works end-to-end  
- Full `ai-prompts/` history + lifecycle docs  

## Security

Synthetic data only. No secrets or real PII in repo, logs, or prompts.
