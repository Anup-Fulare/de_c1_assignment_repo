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

    if df.rdd.isEmpty():
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
    spark = get_spark()
    try:
        dbutils.widgets.text(  # type: ignore[name-defined]
            "source_path",
            "/FileStore/medallion_pipeline/data/products.csv",
            "Products CSV path",
        )
        source_path = dbutils.widgets.get("source_path")  # type: ignore[name-defined]
    except Exception:
        source_path = "/FileStore/medallion_pipeline/data/products.csv"

    ingest_products(spark, source_path)


if __name__ == "__main__":
    main()
