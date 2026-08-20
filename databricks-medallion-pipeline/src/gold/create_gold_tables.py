"""
Create Gold aggregation tables from SQL files.

Databricks Free/Community Edition (Spark Connect compatible):
- No rdd / _jvm / dbutils.fs
- CREATE OR REPLACE (idempotent)
- Empty Silver check via limit(1).count()

Run after Silver exists. Prints row counts per gold.* table.
"""

from __future__ import annotations

from pathlib import Path

from pyspark.sql import SparkSession

SQL_FILES = [
    "01_sales_by_product.sql",
    "02_revenue_by_customer.sql",
    "03_daily_weekly_trends.sql",
    "04_customer_segmentation.sql",
]

GOLD_TABLES = [
    "gold.sales_by_product",
    "gold.revenue_by_customer",
    "gold.daily_weekly_trends",
    "gold.customer_segmentation",
]


def get_spark() -> SparkSession:
    return SparkSession.builder.getOrCreate()


def _gold_sql_dir() -> Path:
    try:
        return Path(__file__).resolve().parent
    except NameError:
        pass
    try:
        from pyspark.dbutils import DBUtils  # type: ignore

        spark = get_spark()
        dbutils = DBUtils(spark)
        user = (
            dbutils.notebook.entry_point.getDbutils()
            .notebook()
            .getContext()
            .userName()
            .get()
        )
        return Path(
            f"/Workspace/Users/{user}/ttn_de_c1_assignment_repo_sync/"
            "databricks-medallion-pipeline/src/gold"
        )
    except Exception:
        import os

        root = os.getenv(
            "REPO_ROOT",
            "/Workspace/Users/default/ttn_de_c1_assignment_repo_sync/"
            "databricks-medallion-pipeline",
        )
        return Path(root) / "src" / "gold"


def _assert_silver(spark: SparkSession) -> None:
    for table in ("silver.orders", "silver.customers", "silver.products"):
        df = spark.table(table)
        if df.limit(1).count() == 0:
            raise ValueError(f"No rows in {table}; run Silver before Gold.")


def create_gold_tables(spark: SparkSession, sql_dir: Path | None = None) -> dict:
    """Execute four Gold SQL scripts; return {table: row_count}."""
    _assert_silver(spark)
    spark.sql("CREATE DATABASE IF NOT EXISTS gold")
    folder = sql_dir or _gold_sql_dir()
    counts: dict[str, int] = {}

    for filename, table in zip(SQL_FILES, GOLD_TABLES):
        path = folder / filename
        sql_text = path.read_text(encoding="utf-8")
        print(f"[Gold] Running {path}")
        spark.sql(sql_text)
        n = spark.table(table).count()
        counts[table] = n
        print(f"[Gold] {table}: rows={n}")

    print("=== Gold create_gold_tables summary ===")
    for table, n in counts.items():
        print(f"  {table}: {n}")
    return counts


def main() -> None:
    create_gold_tables(get_spark())


if __name__ == "__main__":
    main()
