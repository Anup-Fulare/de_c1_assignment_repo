"""
Silver completeness checks. Flag NULLs in critical fields; do not delete rows.

Databricks Free/Community Edition (Spark Connect compatible):
- No JVM / rdd / dbutils.fs
- Empty checks via limit(1).count()

Critical fields (data-quality-strategy.md):
- customers.email
- orders.customer_id
- orders.product_id

Threshold: >99% complete. All failing rows are flagged.
"""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


CHECK_NAME = "completeness"
THRESHOLD_PCT = 99.0


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


def flag_customers_completeness(customers: DataFrame) -> tuple[DataFrame, dict]:
    """Add flag_completeness where email is NULL. Rows are never dropped."""
    flagged = customers.withColumn(
        "flag_completeness", F.col("email").isNull()
    )
    total = flagged.count()
    failed = flagged.filter(F.col("flag_completeness")).count()
    return flagged, _metrics(total, failed, "customers")


def flag_orders_completeness(orders: DataFrame) -> tuple[DataFrame, dict]:
    """Flag if customer_id or product_id is NULL. Rows are never dropped."""
    flagged = orders.withColumn(
        "flag_completeness",
        F.col("customer_id").isNull() | F.col("product_id").isNull(),
    )
    total = flagged.count()
    failed = flagged.filter(F.col("flag_completeness")).count()
    return flagged, _metrics(total, failed, "orders")


def run_completeness(
    spark: SparkSession,
    customers_table: str = "bronze.customers",
    orders_table: str = "bronze.orders",
) -> dict:
    """
    Run completeness on Bronze tables (read-only). Returns metrics list.
    Does not write Silver — create_silver_tables.py will persist flags.
    """
    customers = spark.table(customers_table)
    orders = spark.table(orders_table)
    if customers.limit(1).count() == 0:
        raise ValueError(f"No rows in {customers_table}")
    if orders.limit(1).count() == 0:
        raise ValueError(f"No rows in {orders_table}")

    _, cust_m = flag_customers_completeness(customers)
    _, ord_m = flag_orders_completeness(orders)
    metrics = [cust_m, ord_m]
    print("=== Completeness metrics ===")
    for m in metrics:
        print(m)
    return {"metrics": metrics}


def main() -> None:
    run_completeness(get_spark())


if __name__ == "__main__":
    main()
