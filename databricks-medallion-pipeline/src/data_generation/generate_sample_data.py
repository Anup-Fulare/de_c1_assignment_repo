"""
Generate synthetic e-commerce CSVs with intentional data-quality issues.

Outputs (under data/ relative to project root databricks-medallion-pipeline/):
  - customers.csv  (~10,000+ rows; includes intentional duplicates)
  - orders.csv     (100,000 rows; intentional nulls/orphans/duplicates)
  - products.csv   (500 rows; clean catalog)

Run from databricks-medallion-pipeline/:
  python src/data_generation/generate_sample_data.py
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

# Reproducible RNG
SEED = 42

N_CUSTOMERS = 10_000
N_ORDERS = 100_000
N_PRODUCTS = 500

# Intentional issue counts (assignment)
NULL_EMAILS = 50
DUP_CUSTOMER_ROWS = 10  # extra rows reusing existing customer_id
NULL_ORDER_CUSTOMER_ID = 100
NULL_ORDER_PRODUCT_ID = 200
ORPHAN_CUSTOMER_ID = 50
ORPHAN_PRODUCT_ID = 30
DUP_ORDER_ID_ROWS = 20

SEGMENTS = ["Premium", "Standard", "Basic"]
STATUSES = ["Pending", "Completed", "Cancelled"]
CATEGORIES = [
    "Electronics",
    "Home",
    "Beauty",
    "Sports",
    "Books",
    "Toys",
    "Grocery",
    "Clothing",
]
COUNTRIES = [
    "US",
    "IN",
    "UK",
    "DE",
    "CA",
    "AU",
    "BR",
    "JP",
    "FR",
    "SG",
]

FIRST_NAMES = [
    "Alex",
    "Jordan",
    "Sam",
    "Taylor",
    "Casey",
    "Riley",
    "Morgan",
    "Avery",
    "Quinn",
    "Jamie",
    "Priya",
    "Arjun",
    "Neha",
    "Omar",
    "Sofia",
    "Lucas",
]
LAST_NAMES = [
    "Smith",
    "Patel",
    "Garcia",
    "Kim",
    "Singh",
    "Brown",
    "Nguyen",
    "Silva",
    "Müller",
    "Chen",
    "Khan",
    "Lopez",
]


def _project_root() -> Path:
    # .../databricks-medallion-pipeline/src/data_generation/this_file.py
    return Path(__file__).resolve().parents[2]


def _random_date(rng: random.Random, start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=rng.randint(0, delta))


def generate_products(rng: random.Random) -> pd.DataFrame:
    rows = []
    for pid in range(1, N_PRODUCTS + 1):
        price = round(rng.uniform(5.0, 500.0), 2)
        cost = round(price * rng.uniform(0.4, 0.8), 2)
        rows.append(
            {
                "product_id": pid,
                "product_name": f"Product_{pid:04d}",
                "category": rng.choice(CATEGORIES),
                "price": price,
                "cost": cost,
                "stock_quantity": rng.randint(0, 5000),
                "reorder_level": rng.randint(10, 200),
            }
        )
    df = pd.DataFrame(rows)
    # Use nullable Int64 dtype to prevent float conversion
    df["product_id"] = df["product_id"].astype("Int64")
    df["stock_quantity"] = df["stock_quantity"].astype("Int64")
    df["reorder_level"] = df["reorder_level"].astype("Int64")
    return df


def generate_customers(rng: random.Random) -> pd.DataFrame:
    """10,000 unique customers, then inject NULL emails and duplicate customer_id rows."""
    start = date(2020, 1, 1)
    end = date(2026, 8, 1)
    rows = []
    for cid in range(1, N_CUSTOMERS + 1):
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        email = f"{first.lower()}.{last.lower()}{cid}@example.com"
        rows.append(
            {
                "customer_id": cid,
                "customer_name": f"{first} {last}",
                "email": email,
                "country": rng.choice(COUNTRIES),
                "signup_date": _random_date(rng, start, end).isoformat(),
                "customer_segment": rng.choice(SEGMENTS),
                "lifetime_value": round(rng.uniform(50.0, 20000.0), 2),
            }
        )
    df = pd.DataFrame(rows)
    
    # Convert integer columns to nullable Int64 dtype
    df["customer_id"] = df["customer_id"].astype("Int64")

    # --- Intentional issues: NULL email (completeness) ---
    null_email_idx = rng.sample(range(len(df)), NULL_EMAILS)
    df.loc[null_email_idx, "email"] = pd.NA

    # --- Intentional issues: duplicate customer_id (uniqueness) ---
    # Append DUP_CUSTOMER_ROWS copies of existing customers (same customer_id).
    # Comment: these rows are intentional duplicates for Silver uniqueness tests.
    dup_source_ids = list(range(1, DUP_CUSTOMER_ROWS + 1))
    dup_rows = df[df["customer_id"].isin(dup_source_ids)].copy()
    # Slight name tweak so the row is visibly a second record for the same id
    dup_rows["customer_name"] = dup_rows["customer_name"] + " (dup)"
    df = pd.concat([df, dup_rows], ignore_index=True)

    return df


def generate_orders(
    rng: random.Random, customers: pd.DataFrame, products: pd.DataFrame
) -> pd.DataFrame:
    """100,000 orders with disjoint intentional DQ issues where possible."""
    # Valid customer ids before duplicate append are 1..N_CUSTOMERS
    valid_customer_ids = list(range(1, N_CUSTOMERS + 1))
    valid_product_ids = products["product_id"].tolist()
    start = date(2023, 1, 1)
    end = date(2026, 8, 1)

    rows = []
    for oid in range(1, N_ORDERS + 1):
        qty = rng.randint(1, 5)
        unit_price = round(rng.uniform(5.0, 500.0), 2)
        status = rng.choices(STATUSES, weights=[0.15, 0.7, 0.15], k=1)[0]
        order_date = _random_date(rng, start, end)
        payment_date = None
        if status == "Completed":
            payment_date = (
                order_date + timedelta(days=rng.randint(0, 7))
            ).isoformat()
        elif status == "Pending":
            payment_date = None
        else:
            # Cancelled: sometimes has payment_date
            payment_date = (
                (order_date + timedelta(days=rng.randint(0, 3))).isoformat()
                if rng.random() < 0.2
                else None
            )

        rows.append(
            {
                "order_id": oid,
                "customer_id": rng.choice(valid_customer_ids),
                "order_date": order_date.isoformat(),
                "product_id": rng.choice(valid_product_ids),
                "quantity": qty,
                "unit_price": unit_price,
                "total_amount": round(qty * unit_price, 2),
                "order_status": status,
                "payment_date": payment_date,
            }
        )
    df = pd.DataFrame(rows)
    
    # Convert integer columns to nullable Int64 dtype to prevent float conversion when NAs are added
    # This ensures integers are written as "5764" not "5764.0" in CSV
    df["order_id"] = df["order_id"].astype("Int64")
    df["customer_id"] = df["customer_id"].astype("Int64")
    df["product_id"] = df["product_id"].astype("Int64")
    df["quantity"] = df["quantity"].astype("Int64")

    # Disjoint index slices for intentional issues
    idx = list(range(len(df)))
    rng.shuffle(idx)
    cursor = 0

    def take(n: int) -> list[int]:
        nonlocal cursor
        out = idx[cursor : cursor + n]
        cursor += n
        return out

    # --- NULL customer_id ---
    for i in take(NULL_ORDER_CUSTOMER_ID):
        df.at[i, "customer_id"] = pd.NA

    # --- NULL product_id ---
    for i in take(NULL_ORDER_PRODUCT_ID):
        df.at[i, "product_id"] = pd.NA

    # --- Orphan customer_id (not in customers 1..N_CUSTOMERS) ---
    orphan_cust_base = N_CUSTOMERS + 10_000
    for j, i in enumerate(take(ORPHAN_CUSTOMER_ID)):
        df.at[i, "customer_id"] = orphan_cust_base + j

    # --- Orphan product_id (not in products) ---
    orphan_prod_base = N_PRODUCTS + 10_000
    for j, i in enumerate(take(ORPHAN_PRODUCT_ID)):
        df.at[i, "product_id"] = orphan_prod_base + j

    # --- Duplicate order_id: force 20 rows to reuse another row's order_id ---
    # Comment: intentional duplicates for Silver uniqueness tests.
    dup_targets = take(DUP_ORDER_ID_ROWS)
    # Source ids that remain unique donors (from remaining shuffled indices)
    donors = take(DUP_ORDER_ID_ROWS)
    for target_i, donor_i in zip(dup_targets, donors):
        df.at[target_i, "order_id"] = int(df.at[donor_i, "order_id"])

    return df


def verify_issues(customers: pd.DataFrame, orders: pd.DataFrame, products: pd.DataFrame) -> dict:
    """Print and return counts of intentional issue types."""
    valid_customer_ids = set(range(1, N_CUSTOMERS + 1))
    # After duplicates, unique set of "real" customers for RI is still 1..N_CUSTOMERS
    # Orphans are ids outside that set (and not null).
    product_ids = set(products["product_id"].tolist())

    null_emails = int(customers["email"].isna().sum())
    cust_id_counts = customers["customer_id"].value_counts()
    dup_customer_ids = int((cust_id_counts > 1).sum())
    # Number of extra duplicate rows = sum(count - 1 for ids with count > 1)
    dup_customer_extra_rows = int((cust_id_counts[cust_id_counts > 1] - 1).sum())

    null_cust = int(orders["customer_id"].isna().sum())
    null_prod = int(orders["product_id"].isna().sum())

    non_null_cust = orders["customer_id"].dropna()
    orphan_cust = int((~non_null_cust.astype(int).isin(valid_customer_ids)).sum())

    non_null_prod = orders["product_id"].dropna()
    orphan_prod = int((~non_null_prod.astype(int).isin(product_ids)).sum())

    oid_counts = orders["order_id"].value_counts()
    dup_order_ids = int((oid_counts > 1).sum())
    dup_order_extra_rows = int((oid_counts[oid_counts > 1] - 1).sum())

    summary = {
        "customers_rows": len(customers),
        "orders_rows": len(orders),
        "products_rows": len(products),
        "null_emails": null_emails,
        "duplicate_customer_id_values": dup_customer_ids,
        "duplicate_customer_extra_rows": dup_customer_extra_rows,
        "null_order_customer_id": null_cust,
        "null_order_product_id": null_prod,
        "orphan_customer_id": orphan_cust,
        "orphan_product_id": orphan_prod,
        "duplicate_order_id_values": dup_order_ids,
        "duplicate_order_extra_rows": dup_order_extra_rows,
    }

    print("=== Verification summary (intentional DQ issues) ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print("Expected: null_emails=50, dup customer extra rows=10,")
    print("  null cust=100, null prod=200, orphan cust=50, orphan prod=30,")
    print("  dup order extra rows=20")
    return summary


def main() -> None:
    rng = random.Random(SEED)
    root = _project_root()
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    products = generate_products(rng)
    customers = generate_customers(rng)
    orders = generate_orders(rng, customers, products)

    products_path = data_dir / "products.csv"
    customers_path = data_dir / "customers.csv"
    orders_path = data_dir / "orders.csv"

    products.to_csv(products_path, index=False)
    customers.to_csv(customers_path, index=False, na_rep="")
    orders.to_csv(orders_path, index=False, na_rep="")

    print(f"Wrote {products_path}")
    print(f"Wrote {customers_path}")
    print(f"Wrote {orders_path}")
    verify_issues(customers, orders, products)


if __name__ == "__main__":
    main()
