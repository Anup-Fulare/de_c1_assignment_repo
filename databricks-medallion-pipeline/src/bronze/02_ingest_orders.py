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
    path = _dbfs_path(source_path)
    try:
        from pyspark.dbutils import DBUtils  # type: ignore

        dbutils = DBUtils(spark)
        fs_path = path.replace("dbfs:", "")
        listing = dbutils.fs.ls(fs_path if fs_path.startswith("/") else f"/{fs_path}")
        if not listing:
            raise FileNotFoundError(f"Source path is empty: {path}")
    except ImportError:
        pass
    except Exception as exc:
        raise FileNotFoundError(f"Source path missing or inaccessible: {path}") from exc
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

    if df.rdd.isEmpty():
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
    spark = get_spark()
    try:
        dbutils.widgets.text(  # type: ignore[name-defined]
            "source_path",
            "/FileStore/medallion_pipeline/data/orders.csv",
            "Orders CSV path",
        )
        source_path = dbutils.widgets.get("source_path")  # type: ignore[name-defined]
    except Exception:
        source_path = "/FileStore/medallion_pipeline/data/orders.csv"

    ingest_orders(spark, source_path)


if __name__ == "__main__":
    main()
