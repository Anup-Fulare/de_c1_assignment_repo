"""
Silver referential integrity. Flag orphan FKs; never delete rows.

Databricks Free/Community Edition (Spark Connect compatible).

Rules (data-quality-strategy.md):
- Non-null orders.customer_id must exist in customers.customer_id
- Non-null orders.product_id must exist in products.product_id
- NULL FKs are completeness issues, not RI failures

Threshold: >99.9% valid.
"""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


CHECK_NAME = "referential_integrity"
THRESHOLD_PCT = 99.9


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


def flag_orders_referential_integrity(
    orders: DataFrame,
    customers: DataFrame,
    products: DataFrame,
) -> tuple[DataFrame, dict]:
    """Flag orders with non-null FKs missing from parent tables."""
    cust_keys = customers.select(
        F.col("customer_id").alias("_valid_customer_id")
    ).dropDuplicates(["_valid_customer_id"])
    prod_keys = products.select(
        F.col("product_id").alias("_valid_product_id")
    ).dropDuplicates(["_valid_product_id"])

    joined = (
        orders.join(
            cust_keys,
            orders["customer_id"] == F.col("_valid_customer_id"),
            "left",
        ).join(
            prod_keys,
            orders["product_id"] == F.col("_valid_product_id"),
            "left",
        )
    )

    orphan_cust = F.col("customer_id").isNotNull() & F.col("_valid_customer_id").isNull()
    orphan_prod = F.col("product_id").isNotNull() & F.col("_valid_product_id").isNull()

    flagged = joined.withColumn(
        "flag_referential_integrity", orphan_cust | orphan_prod
    ).drop("_valid_customer_id", "_valid_product_id")

    total = flagged.count()
    failed = flagged.filter(F.col("flag_referential_integrity")).count()
    return flagged, _metrics(total, failed, "orders")


def run_referential_integrity(
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

    _, metrics = flag_orders_referential_integrity(orders, customers, products)
    print("=== Referential integrity metrics ===")
    print(metrics)
    return {"metrics": [metrics]}


def main() -> None:
    run_referential_integrity(get_spark())


if __name__ == "__main__":
    main()
