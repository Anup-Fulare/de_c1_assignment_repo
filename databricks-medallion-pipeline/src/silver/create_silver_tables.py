"""
Create Silver tables and quality metrics report.

Reads Bronze, applies checks 01–05 (flag only, never delete), writes silver.*
and silver.quality_metrics. Spark Connect / Databricks CE compatible.

Run on Databricks after Bronze ingest.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
)

_SILVER_DIR = Path(__file__).resolve().parent
if str(_SILVER_DIR) not in sys.path:
    sys.path.insert(0, str(_SILVER_DIR))

_q01 = import_module("01_quality_completeness")
_q02 = import_module("02_quality_uniqueness")
_q03 = import_module("03_quality_type_validation")
_q04 = import_module("04_quality_referential_integrity")
_q05 = import_module("05_quality_business_logic")

EXPECTED_ISSUES = {
    "customers_null_email": 50,
    "customers_duplicate_rows_flagged": 20,
    "orders_null_customer_id": 100,
    "orders_null_product_id": 200,
    "orders_orphan_customer_id": 50,
    "orders_orphan_product_id": 30,
    "orders_duplicate_rows_flagged": 40,
}


def get_spark() -> SparkSession:
    return SparkSession.builder.getOrCreate()


def _finalize_silver(df: DataFrame, flag_cols: list[str]) -> DataFrame:
    any_fail = F.lit(False)
    for col in flag_cols:
        any_fail = any_fail | F.coalesce(F.col(col), F.lit(False))

    reason_exprs = [
        F.when(F.coalesce(F.col(c), F.lit(False)), F.lit(c.replace("flag_", "")))
        for c in flag_cols
    ]
    reasons_str = F.concat_ws("|", *reason_exprs)

    return df.withColumn(
        "quality_check_result",
        F.when(any_fail, F.lit("FAIL")).otherwise(F.lit("PASS")),
    ).withColumn(
        "quality_failure_reasons",
        F.when(any_fail, reasons_str).otherwise(F.lit(None)),
    )


def build_silver_customers(customers: DataFrame) -> tuple[DataFrame, list[dict]]:
    metrics: list[dict] = []
    df = customers
    df, m = _q01.flag_customers_completeness(df)
    metrics.append(m)
    df, m = _q02.flag_customers_uniqueness(df)
    metrics.append(m)
    df, m = _q03.flag_customers_type_validation(df)
    metrics.append(m)
    df = df.withColumn("flag_referential_integrity", F.lit(False))
    df, m = _q05.flag_customers_business_logic(df)
    metrics.append(m)
    flag_cols = [
        "flag_completeness",
        "flag_uniqueness",
        "flag_type_validation",
        "flag_referential_integrity",
        "flag_business_logic",
    ]
    return _finalize_silver(df, flag_cols), metrics


def build_silver_orders(
    orders: DataFrame,
    customers: DataFrame,
    products: DataFrame,
) -> tuple[DataFrame, list[dict]]:
    metrics: list[dict] = []
    df = orders
    df, m = _q01.flag_orders_completeness(df)
    metrics.append(m)
    df, m = _q02.flag_orders_uniqueness(df)
    metrics.append(m)
    df, m = _q03.flag_orders_type_validation(df)
    metrics.append(m)
    df, m = _q04.flag_orders_referential_integrity(df, customers, products)
    metrics.append(m)
    df, m = _q05.flag_orders_business_logic(df)
    metrics.append(m)
    flag_cols = [
        "flag_completeness",
        "flag_uniqueness",
        "flag_type_validation",
        "flag_referential_integrity",
        "flag_business_logic",
    ]
    return _finalize_silver(df, flag_cols), metrics


def build_silver_products(products: DataFrame) -> tuple[DataFrame, list[dict]]:
    metrics: list[dict] = []
    df, m = _q03.flag_products_type_validation(products)
    metrics.append(m)
    df = (
        df.withColumn("flag_completeness", F.lit(False))
        .withColumn("flag_uniqueness", F.lit(False))
        .withColumn("flag_referential_integrity", F.lit(False))
        .withColumn("flag_business_logic", F.lit(False))
    )
    flag_cols = [
        "flag_completeness",
        "flag_uniqueness",
        "flag_type_validation",
        "flag_referential_integrity",
        "flag_business_logic",
    ]
    return _finalize_silver(df, flag_cols), metrics


def _count_orphan_customers(orders: DataFrame, customers: DataFrame) -> int:
    valid = customers.select(F.col("customer_id").alias("_cid")).distinct()
    return (
        orders.filter(F.col("customer_id").isNotNull())
        .join(valid, orders.customer_id == F.col("_cid"), "left_anti")
        .count()
    )


def _count_orphan_products(orders: DataFrame, products: DataFrame) -> int:
    valid = products.select(F.col("product_id").alias("_pid")).distinct()
    return (
        orders.filter(F.col("product_id").isNotNull())
        .join(valid, orders.product_id == F.col("_pid"), "left_anti")
        .count()
    )


def prove_intentional_detection(
    silver_customers: DataFrame,
    silver_orders: DataFrame,
    silver_products: DataFrame,
) -> None:
    actual = {
        "customers_null_email": silver_customers.filter(F.col("email").isNull()).count(),
        "customers_duplicate_rows_flagged": silver_customers.filter(
            F.col("flag_uniqueness")
        ).count(),
        "orders_null_customer_id": silver_orders.filter(
            F.col("customer_id").isNull()
        ).count(),
        "orders_null_product_id": silver_orders.filter(
            F.col("product_id").isNull()
        ).count(),
        "orders_orphan_customer_id": _count_orphan_customers(
            silver_orders, silver_customers
        ),
        "orders_orphan_product_id": _count_orphan_products(
            silver_orders, silver_products
        ),
        "orders_duplicate_rows_flagged": silver_orders.filter(
            F.col("flag_uniqueness")
        ).count(),
    }
    print("=== Intentional issue detection proof ===")
    all_ok = True
    for key, expected in EXPECTED_ISSUES.items():
        got = actual[key]
        ok = got == expected
        all_ok = all_ok and ok
        status = "OK" if ok else "MISMATCH"
        print(f"  {key}: expected={expected}, actual={got} [{status}]")
    if all_ok:
        print("All intentional issue counts detected as expected.")
    else:
        print("WARNING: review counts vs seeded inventory.")


def write_metrics_table(spark: SparkSession, metrics: list[dict]) -> None:
    rows = [
        (
            m["check_name"],
            m["table_name"],
            int(m["total_rows_evaluated"]),
            int(m["failed_rows"]),
            float(m["pct_passed"]),
        )
        for m in metrics
    ]
    schema = StructType(
        [
            StructField("check_name", StringType(), False),
            StructField("table_name", StringType(), False),
            StructField("total_rows_evaluated", LongType(), False),
            StructField("failed_rows", LongType(), False),
            StructField("pct_passed", DoubleType(), False),
        ]
    )
    report_df = spark.createDataFrame(rows, schema).withColumn(
        "report_ts", F.current_timestamp()
    )
    spark.sql("CREATE DATABASE IF NOT EXISTS silver")
    report_df.write.format("delta").mode("overwrite").saveAsTable(
        "silver.quality_metrics"
    )
    print("=== Quality metrics report (silver.quality_metrics) ===")
    spark.table("silver.quality_metrics").show(truncate=False)


def create_silver_tables(
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

    silver_cust, m_cust = build_silver_customers(customers)
    silver_ord, m_ord = build_silver_orders(orders, customers, products)
    silver_prod, m_prod = build_silver_products(products)
    all_metrics = m_cust + m_ord + m_prod

    spark.sql("CREATE DATABASE IF NOT EXISTS silver")
    for table_name, sdf in [
        ("silver.customers", silver_cust),
        ("silver.orders", silver_ord),
        ("silver.products", silver_prod),
    ]:
        sdf.write.format("delta").mode("overwrite").option(
            "overwriteSchema", "true"
        ).saveAsTable(table_name)
        n = sdf.count()
        fail_n = sdf.filter(F.col("quality_check_result") == "FAIL").count()
        print(f"Wrote {table_name}: rows={n}, FAIL rows={fail_n}")

    write_metrics_table(spark, all_metrics)
    prove_intentional_detection(silver_cust, silver_ord, silver_prod)
    return {"metrics": all_metrics}


def main() -> None:
    create_silver_tables(get_spark())


if __name__ == "__main__":
    main()
