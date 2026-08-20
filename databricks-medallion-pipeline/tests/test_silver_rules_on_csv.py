"""
Silver-equivalent DQ rules on local CSVs (pandas).

Mirrors src/silver completeness, uniqueness, and referential integrity
so seeded issues are detectable without Spark/Databricks.

Run from databricks-medallion-pipeline/:
  python tests/test_silver_rules_on_csv.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

N_CUSTOMERS = 10_000


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def _load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    data = _data_dir()
    customers = pd.read_csv(data / "customers.csv", keep_default_na=True)
    orders = pd.read_csv(data / "orders.csv", keep_default_na=True)
    products = pd.read_csv(data / "products.csv", keep_default_na=True)
    return customers, orders, products


def flag_completeness_customers(customers: pd.DataFrame) -> pd.Series:
    """Same as silver: NULL email."""
    return customers["email"].isna()


def flag_completeness_orders(orders: pd.DataFrame) -> pd.Series:
    """Same as silver: NULL customer_id or product_id."""
    return orders["customer_id"].isna() | orders["product_id"].isna()


def flag_uniqueness(df: pd.DataFrame, key: str) -> pd.Series:
    """Same as silver: every row whose key appears more than once."""
    return df.groupby(key)[key].transform("count") > 1


def flag_ri_orphan_customers(orders: pd.DataFrame, customers: pd.DataFrame) -> pd.Series:
    """Non-null customer_id not in customers (valid ids 1..N_CUSTOMERS plus dup copies)."""
    valid = set(customers["customer_id"].dropna().astype(int).tolist())
    cid = orders["customer_id"]
    return cid.notna() & ~cid.astype("Int64").isin(valid)


def flag_ri_orphan_products(orders: pd.DataFrame, products: pd.DataFrame) -> pd.Series:
    valid = set(products["product_id"].dropna().astype(int).tolist())
    pid = orders["product_id"]
    return pid.notna() & ~pid.astype("Int64").isin(valid)


def test_completeness_detects_seeded_nulls() -> None:
    customers, orders, _ = _load()
    assert int(flag_completeness_customers(customers).sum()) == 50
    assert int(orders["customer_id"].isna().sum()) == 100
    assert int(orders["product_id"].isna().sum()) == 200
    # Disjoint slices → 300 completeness flags on orders
    assert int(flag_completeness_orders(orders).sum()) == 300


def test_uniqueness_detects_duplicate_keys() -> None:
    customers, orders, _ = _load()
    # 10 duplicate ids × 2 rows = 20 flagged customer rows
    assert int(flag_uniqueness(customers, "customer_id").sum()) == 20
    # 20 duplicate ids × 2 rows = 40 flagged order rows
    assert int(flag_uniqueness(orders, "order_id").sum()) == 40


def test_referential_integrity_detects_orphans() -> None:
    customers, orders, products = _load()
    # Valid customer_id set includes duplicate copies of ids 1..10
    assert int(flag_ri_orphan_customers(orders, customers).sum()) == 50
    assert int(flag_ri_orphan_products(orders, products).sum()) == 30


def test_null_fks_are_not_counted_as_orphans() -> None:
    customers, orders, products = _load()
    orphan_c = flag_ri_orphan_customers(orders, customers)
    orphan_p = flag_ri_orphan_products(orders, products)
    assert not bool((orphan_c & orders["customer_id"].isna()).any())
    assert not bool((orphan_p & orders["product_id"].isna()).any())


if __name__ == "__main__":
    tests = [
        test_completeness_detects_seeded_nulls,
        test_uniqueness_detects_duplicate_keys,
        test_referential_integrity_detects_orphans,
        test_null_fks_are_not_counted_as_orphans,
    ]
    for fn in tests:
        fn()
        print(f"PASSED {fn.__name__}")
    print("All Silver-rule-on-CSV assertions PASSED.")
