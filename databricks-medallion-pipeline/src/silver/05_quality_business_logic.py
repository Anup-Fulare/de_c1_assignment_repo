"""
Silver business-logic checks. Flag only; never delete.

Databricks Free/Community Edition (Spark Connect compatible).

Rules (data-quality-strategy.md):
- orders.total_amount ≈ quantity * unit_price (tolerance 0.01)
- Completed orders should have payment_date
- customers.signup_date is not far in the future (> current_date + 1 day)

Threshold: >99% valid.
"""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


CHECK_NAME = "business_logic"
THRESHOLD_PCT = 99.0
AMOUNT_TOLERANCE = 0.01


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


def flag_customers_business_logic(customers: DataFrame) -> tuple[DataFrame, dict]:
    """Flag signup_date more than one day in the future."""
    future = F.col("signup_date") > F.date_add(F.current_date(), 1)
    flagged = customers.withColumn(
        "flag_business_logic", F.coalesce(future, F.lit(False))
    )
    total = flagged.count()
    failed = flagged.filter(F.col("flag_business_logic")).count()
    return flagged, _metrics(total, failed, "customers")


def flag_orders_business_logic(orders: DataFrame) -> tuple[DataFrame, dict]:
    """Flag amount mismatch (when qty/price/amount present) or Completed without payment_date."""
    expected = F.col("quantity") * F.col("unit_price")
    amount_mismatch = (
        F.col("quantity").isNotNull()
        & F.col("unit_price").isNotNull()
        & F.col("total_amount").isNotNull()
        & (F.abs(F.col("total_amount") - expected) > F.lit(AMOUNT_TOLERANCE))
    )
    completed_no_pay = (F.col("order_status") == F.lit("Completed")) & F.col(
        "payment_date"
    ).isNull()
    flagged = orders.withColumn(
        "flag_business_logic",
        F.coalesce(amount_mismatch | completed_no_pay, F.lit(False)),
    )
    total = flagged.count()
    failed = flagged.filter(F.col("flag_business_logic")).count()
    return flagged, _metrics(total, failed, "orders")


def run_business_logic(
    spark: SparkSession,
    customers_table: str = "bronze.customers",
    orders_table: str = "bronze.orders",
) -> dict:
    customers = spark.table(customers_table)
    orders = spark.table(orders_table)
    if customers.limit(1).count() == 0:
        raise ValueError(f"No rows in {customers_table}")
    if orders.limit(1).count() == 0:
        raise ValueError(f"No rows in {orders_table}")

    _, c = flag_customers_business_logic(customers)
    _, o = flag_orders_business_logic(orders)
    metrics = [c, o]
    print("=== Business logic metrics ===")
    for m in metrics:
        print(m)
    return {"metrics": metrics}


def main() -> None:
    run_business_logic(get_spark())


if __name__ == "__main__":
    main()
