"""
Bronze ingest: customers (raw, no cleaning).

Databricks Free/Community Edition — run as a notebook or job.
Does NOT drop/fix nulls, duplicates, or other quality issues.

Expected CSV columns: customer_id, customer_name, email, country,
signup_date, customer_segment, lifetime_value

Target table: bronze.customers
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
    """Normalize to a Spark-readable path."""
    if path.startswith("dbfs:"):
        return path
    if path.startswith("/"):
        return f"dbfs:{path}"
    return f"dbfs:/{path.lstrip('/')}"


def validate_source(spark: SparkSession, source_path: str) -> str:
    """Validate source path - Spark Connect compatible (no JVM/dbutils)."""
    path = _dbfs_path(source_path)
    # Skip file validation on Spark Connect - DataFrame load will fail if missing
    return path


CUSTOMER_SCHEMA = StructType(
    [
        StructField("customer_id", IntegerType(), True),
        StructField("customer_name", StringType(), True),
        StructField("email", StringType(), True),
        StructField("country", StringType(), True),
        StructField("signup_date", StringType(), True),  # cast to date after read
        StructField("customer_segment", StringType(), True),
        StructField("lifetime_value", DecimalType(18, 2), True),
    ]
)


def ingest_customers(
    spark: SparkSession,
    source_path: str,
    target_table: str = "bronze.customers",
) -> dict:
    """
    Read raw customers CSV → bronze.customers Delta table.
    No cleaning: null emails and duplicate customer_ids are preserved.
    """
    path = validate_source(spark, source_path)
    ingest_ts = F.current_timestamp()

    df = (
        spark.read.format("csv")
        .option("header", "true")
        .option("nullValue", "")
        .schema(CUSTOMER_SCHEMA)
        .load(path)
    )

    # Check for empty dataframe - Spark Connect compatible
    if df.limit(1).count() == 0:
        raise ValueError(f"No rows found at {path}")

    bronze_df = (
        df.withColumn("signup_date", F.to_date(F.col("signup_date")))
        .withColumn("_ingest_source_path", F.lit(path))
        .withColumn("_ingest_ts", ingest_ts)
    )

    # Ensure database exists (CE-friendly)
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
    print(f"[Bronze] customers ingest OK: {meta}")
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
        source_path = f"{repo_root}/data/customers.csv"
    except Exception:
        # Fallback for non-notebook execution
        import os
        repo_root = os.getenv("REPO_ROOT", "/Workspace/Users/default/ttn_de_c1_assignment_repo_sync/databricks-medallion-pipeline")
        source_path = f"{repo_root}/data/customers.csv"
    
    # Allow override via widget if in notebook
    try:
        dbutils.widgets.text("source_path", source_path, "Customers CSV path")  # type: ignore[name-defined]
        source_path = dbutils.widgets.get("source_path")  # type: ignore[name-defined]
    except Exception:
        pass

    ingest_customers(spark, source_path)


if __name__ == "__main__":
    main()
