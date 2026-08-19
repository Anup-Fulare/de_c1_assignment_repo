"""
Bronze ingest: orders (raw, no cleaning).

Databricks Free/Community Edition — run as a notebook or job.
Does NOT drop/fix null FKs, orphans, or duplicate order_ids.

Target table: bronze.orders
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DecimalType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)


def get_spark() -> SparkSession:
    return SparkSession.builder.getOrCreate()


def _dbfs_path(path: str) -> str:
    if path.startswith("dbfs:"):
        return path
    if path.startswith("/"):
        return f"dbfs:{path}"
    return f"dbfs:/{path.lstrip('/')}"


def validate_source(spark: SparkSession, source_path: str) -> str:
    """Validate source path - Spark Connect compatible (no dbutils)."""
    path = _dbfs_path(source_path)
    # Skip file validation on Spark Connect - DataFrame load will fail if missing
    return path


ORDER_SCHEMA = StructType(
    [
        StructField("order_id", IntegerType(), True),
        StructField("customer_id", IntegerType(), True),
        StructField("order_date", StringType(), True),
        StructField("product_id", IntegerType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("unit_price", DecimalType(18, 2), True),
        StructField("total_amount", DecimalType(18, 2), True),
        StructField("order_status", StringType(), True),
        StructField("payment_date", StringType(), True),
    ]
)


def ingest_orders(
    spark: SparkSession,
    source_path: str,
    target_table: str = "bronze.orders",
) -> dict:
    """Read raw orders CSV → bronze.orders. Preserve all bad rows."""
    path = validate_source(spark, source_path)
    ingest_ts = F.current_timestamp()

    df = (
        spark.read.format("csv")
        .option("header", "true")
        .option("nullValue", "")
        .schema(ORDER_SCHEMA)
        .load(path)
    )

    # Check for empty dataframe - Spark Connect compatible
    if df.limit(1).count() == 0:
        raise ValueError(f"No rows found at {path}")

    bronze_df = (
        df.withColumn("order_date", F.to_date(F.col("order_date")))
        .withColumn("payment_date", F.to_date(F.col("payment_date")))
        .withColumn("_ingest_source_path", F.lit(path))
        .withColumn("_ingest_ts", ingest_ts)
    )

    spark.sql("CREATE DATABASE IF NOT EXISTS bronze")
    (
        bronze_df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(target_table)
    )

    row_count = bronze_df.count()
    meta = {
        "table": target_table,
        "source_path": path,
        "row_count": row_count,
        "ingest_ts": str(spark.sql("SELECT current_timestamp() AS ts").collect()[0]["ts"]),
    }
    print(f"[Bronze] orders ingest OK: {meta}")
    return meta


def main() -> None:
    """Main entry point - auto-detects user path for portability."""
    spark = get_spark()
    
    # Auto-detect user and repository location
    try:
        from pyspark.dbutils import DBUtils  # type: ignore
        dbutils = DBUtils(spark)
        current_user = dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()
        repo_root = f"/Workspace/Users/{current_user}/ttn_de_c1_assignment_repo_sync/databricks-medallion-pipeline"
        source_path = f"{repo_root}/data/orders.csv"
    except Exception:
        # Fallback for non-notebook execution
        import os
        repo_root = os.getenv("REPO_ROOT", "/Workspace/Users/default/ttn_de_c1_assignment_repo_sync/databricks-medallion-pipeline")
        source_path = f"{repo_root}/data/orders.csv"
    
    # Allow override via widget if in notebook
    try:
        dbutils.widgets.text("source_path", source_path, "Orders CSV path")  # type: ignore[name-defined]
        source_path = dbutils.widgets.get("source_path")  # type: ignore[name-defined]
    except Exception:
        pass

    ingest_orders(spark, source_path)


if __name__ == "__main__":
    main()
