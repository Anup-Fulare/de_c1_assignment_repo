"""
Bronze ingest: products (raw, no cleaning).

Databricks Free/Community Edition — run as a notebook or job.
Products catalog is expected clean; still no transforms beyond type casts.

Target table: bronze.products
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


PRODUCT_SCHEMA = StructType(
    [
        StructField("product_id", IntegerType(), True),
        StructField("product_name", StringType(), True),
        StructField("category", StringType(), True),
        StructField("price", DecimalType(18, 2), True),
        StructField("cost", DecimalType(18, 2), True),
        StructField("stock_quantity", IntegerType(), True),
        StructField("reorder_level", IntegerType(), True),
    ]
)


def ingest_products(
    spark: SparkSession,
    source_path: str,
    target_table: str = "bronze.products",
) -> dict:
    """Read raw products CSV → bronze.products."""
    path = validate_source(spark, source_path)
    ingest_ts = F.current_timestamp()

    df = (
        spark.read.format("csv")
        .option("header", "true")
        .option("nullValue", "")
        .schema(PRODUCT_SCHEMA)
        .load(path)
    )

    # Check for empty dataframe - Spark Connect compatible
    if df.limit(1).count() == 0:
        raise ValueError(f"No rows found at {path}")

    bronze_df = df.withColumn("_ingest_source_path", F.lit(path)).withColumn(
        "_ingest_ts", ingest_ts
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
    print(f"[Bronze] products ingest OK: {meta}")
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
        source_path = f"{repo_root}/data/products.csv"
    except Exception:
        # Fallback for non-notebook execution
        import os
        repo_root = os.getenv("REPO_ROOT", "/Workspace/Users/default/ttn_de_c1_assignment_repo_sync/databricks-medallion-pipeline")
        source_path = f"{repo_root}/data/products.csv"
    
    # Allow override via widget if in notebook
    try:
        dbutils.widgets.text("source_path", source_path, "Products CSV path")  # type: ignore[name-defined]
        source_path = dbutils.widgets.get("source_path")  # type: ignore[name-defined]
    except Exception:
        pass

    ingest_products(spark, source_path)


if __name__ == "__main__":
    main()
