"""Assert intentional DQ issue counts on generated sample CSVs.

Run from databricks-medallion-pipeline/:
  python -m pytest tests/test_sample_data_issues.py -q
  # or without pytest:
  python tests/test_sample_data_issues.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

N_CUSTOMERS = 10_000
N_PRODUCTS = 500

EXPECTED = {
    "null_emails": 50,
    "duplicate_customer_extra_rows": 10,
    "null_order_customer_id": 100,
    "null_order_product_id": 200,
    "orphan_customer_id": 50,
    "orphan_product_id": 30,
    "duplicate_order_extra_rows": 20,
    "products_rows": 500,
    "orders_rows": 100_000,
}


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def _load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    data = _data_dir()
    customers = pd.read_csv(data / "customers.csv", keep_default_na=True)
    orders = pd.read_csv(data / "orders.csv", keep_default_na=True)
    products = pd.read_csv(data / "products.csv", keep_default_na=True)
    return customers, orders, products


def measure_issues(
    customers: pd.DataFrame, orders: pd.DataFrame, products: pd.DataFrame
) -> dict[str, int]:
    valid_customer_ids = set(range(1, N_CUSTOMERS + 1))
    product_ids = set(products["product_id"].tolist())

    cust_id_counts = customers["customer_id"].value_counts()
    dup_customer_extra = int((cust_id_counts[cust_id_counts > 1] - 1).sum())

    oid_counts = orders["order_id"].value_counts()
    dup_order_extra = int((oid_counts[oid_counts > 1] - 1).sum())

    non_null_cust = orders["customer_id"].dropna()
    orphan_cust = int((~non_null_cust.astype(int).isin(valid_customer_ids)).sum())

    non_null_prod = orders["product_id"].dropna()
    orphan_prod = int((~non_null_prod.astype(int).isin(product_ids)).sum())

    return {
        "null_emails": int(customers["email"].isna().sum()),
        "duplicate_customer_extra_rows": dup_customer_extra,
        "null_order_customer_id": int(orders["customer_id"].isna().sum()),
        "null_order_product_id": int(orders["product_id"].isna().sum()),
        "orphan_customer_id": orphan_cust,
        "orphan_product_id": orphan_prod,
        "duplicate_order_extra_rows": dup_order_extra,
        "products_rows": len(products),
        "orders_rows": len(orders),
        "customers_rows": len(customers),
    }


def test_intentional_dq_issue_counts() -> None:
    customers, orders, products = _load()
    actual = measure_issues(customers, orders, products)

    assert actual["products_rows"] == EXPECTED["products_rows"]
    assert actual["orders_rows"] == EXPECTED["orders_rows"]
    # 10,000 unique + 10 duplicate rows
    assert actual["customers_rows"] == N_CUSTOMERS + EXPECTED["duplicate_customer_extra_rows"]

    for key, expected in EXPECTED.items():
        if key in ("products_rows", "orders_rows"):
            continue
        assert actual[key] == expected, f"{key}: expected {expected}, got {actual[key]}"


def test_products_catalog_is_clean() -> None:
    _, _, products = _load()
    assert products["product_id"].is_unique
    assert products["product_id"].between(1, N_PRODUCTS).all()


if __name__ == "__main__":
    customers, orders, products = _load()
    actual = measure_issues(customers, orders, products)
    print("=== Actual intentional DQ issue counts ===")
    for k, v in actual.items():
        print(f"  {k}: {v}")

    failures = []
    assert_keys = [
        "null_emails",
        "duplicate_customer_extra_rows",
        "null_order_customer_id",
        "null_order_product_id",
        "orphan_customer_id",
        "orphan_product_id",
        "duplicate_order_extra_rows",
        "products_rows",
        "orders_rows",
    ]
    for key in assert_keys:
        if actual[key] != EXPECTED[key]:
            failures.append(f"{key}: expected {EXPECTED[key]}, got {actual[key]}")
    if actual["customers_rows"] != N_CUSTOMERS + EXPECTED["duplicate_customer_extra_rows"]:
        failures.append(
            f"customers_rows: expected {N_CUSTOMERS + EXPECTED['duplicate_customer_extra_rows']}, "
            f"got {actual['customers_rows']}"
        )

    if failures:
        print("FAILED:")
        for f in failures:
            print(f"  - {f}")
        raise SystemExit(1)

    print("All intentional DQ issue count assertions PASSED.")
