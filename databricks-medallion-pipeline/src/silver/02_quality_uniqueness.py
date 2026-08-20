"""
Silver uniqueness checks. Flag duplicate business keys; do not delete rows.

Databricks Free/Community Edition (Spark Connect compatible):
- No JVM / rdd / dbutils.fs

Keys (data-quality-strategy.md):
- customers.customer_id
- orders.order_id

Any row whose key appears more than once is flagged (including both copies).
Threshold: 100% unique.
"""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F


CHECK_NAME = "uniqueness"
THRESHOLD_PCT = 100.0


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
        "threshold_met": pct >= THRESHOLD_PCT,
    }


def flag_customers_uniqueness(customers: DataFrame) -> tuple[DataFrame, dict]:
    """Flag rows whose customer_id occurs more than once. Never drop rows."""
    w = Window.partitionBy("customer_id")
    flagged = customers.withColumn(
        "flag_uniqueness", F.count(F.lit(1)).over(w) > 1
    )
    total = flagged.count()
    failed = flagged.filter(F.col("flag_uniqueness")).count()
    return flagged, _metrics(total, failed, "customers")


def flag_orders_uniqueness(orders: DataFrame) -> tuple[DataFrame, dict]:
    """Flag rows whose order_id occurs more than once. Never drop rows."""
    w = Window.partitionBy("order_id")
    flagged = orders.withColumn(
        "flag_uniqueness", F.count(F.lit(1)).over(w) > 1
    )
    total = flagged.count()
    failed = flagged.filter(F.col("flag_uniqueness")).count()
    return flagged, _metrics(total, failed, "orders")


def run_uniqueness(
    spark: SparkSession,
    customers_table: str = "bronze.customers",
    orders_table: str = "bronze.orders",
) -> dict:
    """Run uniqueness on Bronze tables (read-only). Does not write Silver."""
    customers = spark.table(customers_table)
    orders = spark.table(orders_table)
    if customers.limit(1).count() == 0:
        raise ValueError(f"No rows in {customers_table}")
    if orders.limit(1).count() == 0:
        raise ValueError(f"No rows in {orders_table}")

    _, cust_m = flag_customers_uniqueness(customers)
    _, ord_m = flag_orders_uniqueness(orders)
    metrics = [cust_m, ord_m]
    print("=== Uniqueness metrics ===")
    for m in metrics:
        print(m)
    return {"metrics": metrics}


def main() -> None:
    run_uniqueness(get_spark())


if __name__ == "__main__":
    main()
