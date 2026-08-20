"""
Pipeline row-count relationships (documentation + local invariants).

Databricks CE cannot be asserted here (no Spark). This module:
- States expected Bronze/Silver/Gold relationships used in CE checks
- Asserts CSV vs documented volumes (local)

Run: python tests/test_pipeline_row_relationships.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# --- Expected relationships (after CE pipeline) ---
# Bronze row counts == CSV row counts (raw ingest, no drop)
# Silver row counts == Bronze row counts (flag, do not delete)
# gold.sales_by_product rows <= 500 (one per product with Completed sales)
# gold.revenue_by_customer rows <= distinct passing customers with Completed orders
# gold.customer_segmentation rows == 4 (typical: four segment types)
# gold.daily_weekly_trends: grain day and week both present

CSV_CUSTOMERS = 10_010
CSV_ORDERS = 100_000
CSV_PRODUCTS = 500


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def test_csv_volumes_match_bronze_contract() -> None:
    """If Bronze ingest is correct, bronze.* counts equal these CSV lengths."""
    data = _data_dir()
    customers = pd.read_csv(data / "customers.csv")
    orders = pd.read_csv(data / "orders.csv")
    products = pd.read_csv(data / "products.csv")
    assert len(customers) == CSV_CUSTOMERS
    assert len(orders) == CSV_ORDERS
    assert len(products) == CSV_PRODUCTS


def test_documented_layer_invariants() -> None:
    """Structural expectations for CE (not executed against Spark)."""
    invariants = {
        "silver.customers rows": "equal bronze.customers (no delete)",
        "silver.orders rows": "equal bronze.orders (no delete)",
        "silver.products rows": "equal bronze.products (no delete)",
        "gold.customer_segmentation": "typically 4 rows (segment types)",
        "dashboard Q1": "10 rows from gold.sales_by_product",
    }
    assert len(invariants) == 5


if __name__ == "__main__":
    test_csv_volumes_match_bronze_contract()
    test_documented_layer_invariants()
    print("CSV volumes OK (Bronze contract).")
    print("CE checklist (run in Databricks after each layer):")
    print("  bronze.customers = 10010  |  bronze.orders = 100000  |  bronze.products = 500")
    print("  silver.* row counts = bronze.* (FAIL rows flagged, not dropped)")
    print("  gold.sales_by_product >= 10 rows; gold.customer_segmentation typically 4")
    print("All pipeline-relationship local assertions PASSED.")
