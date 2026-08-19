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
    path = _dbfs_path(source_path)
    try:
        files = spark._jvm.org.apache.hadoop.fs.FileSystem.get(
            spark._jsc.hadoopConfiguration()
        )
        uri = spark._jvm.java.net.URI(path.replace("dbfs:", "dbfs://"))
        # Prefer dbutils when available (Databricks notebooks)
    except Exception:
        pass

    # Lightweight existence check via Spark read attempt after listing with dbutils if present
    try:
        from pyspark.dbutils import DBUtils  # type: ignore

        dbutils = DBUtils(spark)
        # path without dbfs: prefix for dbutils.fs
        fs_path = path.replace("dbfs:", "")
        listing = dbutils.fs.ls(fs_path if fs_path.startswith("/") else f"/{fs_path}")
        if not listing:
            raise FileNotFoundError(f"Source path is empty: {path}")
    except ImportError:
        # Local/unit context without dbutils — skip FS list; read will fail clearly
        pass
    except Exception as exc:
        raise FileNotFoundError(f"Source path missing or inaccessible: {path}") from exc

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

    if df.rdd.isEmpty():
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
    spark = get_spark()
    # Databricks widget (ignored outside notebooks)
    try:
        dbutils.widgets.text(  # type: ignore[name-defined]
            "source_path",
            "/FileStore/medallion_pipeline/data/customers.csv",
            "Customers CSV path",
        )
        source_path = dbutils.widgets.get("source_path")  # type: ignore[name-defined]
    except Exception:
        source_path = "/FileStore/medallion_pipeline/data/customers.csv"

    ingest_customers(spark, source_path)


if __name__ == "__main__":
    main()
