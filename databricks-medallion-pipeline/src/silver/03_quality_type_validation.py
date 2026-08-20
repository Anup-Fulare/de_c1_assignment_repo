"""
Silver type / range / format validation. Flag only; never delete.

Databricks Free/Community Edition (Spark Connect compatible).

Rules (data-quality-strategy.md):
- Email format when present (simple local@domain check)
- customer_segment in Premium / Standard / Basic
- quantity, unit_price, total_amount, price, cost >= 0
- order_status in Pending / Completed / Cancelled
- dates already stored as DATE in Bronze; null date after ingest is a type fail
  for required date fields (signup_date, order_date)

Threshold: >99% valid.
"""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


CHECK_NAME = "type_validation"
THRESHOLD_PCT = 99.0
SEGMENTS = ["Premium", "Standard", "Basic"]
STATUSES = ["Pending", "Completed", "Cancelled"]
# Simple email: has @ and a dot after @, no spaces
EMAIL_RE = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


def get_spark() -> SparkSession:
    return SparkSession.builder.getOrCreate()


def _metrics(total: int, failed: int, table_name: str) -> dict:
    passed = total - failed
    pct = (passed / total * 100.0) if total else 100.0
    return {
        "check_name": CHECK_NAME,
        "table_name": table_name,
        "total_rows_evaluated": total,
        "failed_rows": failed,
        "pct_passed": round(pct, 4),
        "threshold_pct": THRESHOLD_PCT,
        "threshold_met": pct > THRESHOLD_PCT,
    }


def flag_customers_type_validation(customers: DataFrame) -> tuple[DataFrame, dict]:
    email_ok = F.col("email").isNull() | F.col("email").rlike(EMAIL_RE)
    segment_ok = F.col("customer_segment").isin(SEGMENTS)
    signup_ok = F.col("signup_date").isNotNull()
    ltv_ok = F.col("lifetime_value").isNull() | (F.col("lifetime_value") >= 0)
    flagged = customers.withColumn(
        "flag_type_validation",
        ~(email_ok & segment_ok & signup_ok & ltv_ok),
    )
    total = flagged.count()
    failed = flagged.filter(F.col("flag_type_validation")).count()
    return flagged, _metrics(total, failed, "customers")


def flag_orders_type_validation(orders: DataFrame) -> tuple[DataFrame, dict]:
    qty_ok = F.col("quantity").isNull() | (F.col("quantity") >= 0)
    price_ok = F.col("unit_price").isNull() | (F.col("unit_price") >= 0)
    amt_ok = F.col("total_amount").isNull() | (F.col("total_amount") >= 0)
    status_ok = F.col("order_status").isin(STATUSES)
    date_ok = F.col("order_date").isNotNull()
    flagged = orders.withColumn(
        "flag_type_validation",
        ~(qty_ok & price_ok & amt_ok & status_ok & date_ok),
    )
    total = flagged.count()
    failed = flagged.filter(F.col("flag_type_validation")).count()
    return flagged, _metrics(total, failed, "orders")


def flag_products_type_validation(products: DataFrame) -> tuple[DataFrame, dict]:
    price_ok = F.col("price").isNull() | (F.col("price") >= 0)
    cost_ok = F.col("cost").isNull() | (F.col("cost") >= 0)
    stock_ok = F.col("stock_quantity").isNull() | (F.col("stock_quantity") >= 0)
    reorder_ok = F.col("reorder_level").isNull() | (F.col("reorder_level") >= 0)
    flagged = products.withColumn(
        "flag_type_validation",
        ~(price_ok & cost_ok & stock_ok & reorder_ok),
    )
    total = flagged.count()
    failed = flagged.filter(F.col("flag_type_validation")).count()
    return flagged, _metrics(total, failed, "products")


def run_type_validation(
    spark: SparkSession,
    customers_table: str = "bronze.customers",
    orders_table: str = "bronze.orders",
    products_table: str = "bronze.products",
) -> dict:
    customers = spark.table(customers_table)
    orders = spark.table(orders_table)
    products = spark.table(products_table)
    for name, df in [
        (customers_table, customers),
        (orders_table, orders),
        (products_table, products),
    ]:
        if df.limit(1).count() == 0:
            raise ValueError(f"No rows in {name}")

    _, c = flag_customers_type_validation(customers)
    _, o = flag_orders_type_validation(orders)
    _, p = flag_products_type_validation(products)
    metrics = [c, o, p]
    print("=== Type validation metrics ===")
    for m in metrics:
        print(m)
    return {"metrics": metrics}


def main() -> None:
    run_type_validation(get_spark())


if __name__ == "__main__":
    main()
