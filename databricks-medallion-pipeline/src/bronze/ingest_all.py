"""
Run all Bronze ingestions in sequence (fail fast).

Target tables (design-notes.md): bronze.customers, bronze.orders, bronze.products

Databricks CE: set widgets for a data directory, then run this file as a job/notebook
after adding the repo `src` folder to sys.path, or copy the three ingest modules
alongside this script.

Default CSV directory: /FileStore/medallion_pipeline/data
"""

from __future__ import annotations

import sys
from pathlib import Path

from pyspark.sql import SparkSession

# Allow `from 01_ingest_customers import ...` when this file lives next to siblings
_BRONZE_DIR = Path(__file__).resolve().parent
if str(_BRONZE_DIR) not in sys.path:
    sys.path.insert(0, str(_BRONZE_DIR))

from importlib import import_module  # noqa: E402

_customers = import_module("01_ingest_customers")
_orders = import_module("02_ingest_orders")
_products = import_module("03_ingest_products")


DEFAULT_DATA_DIR = "/FileStore/medallion_pipeline/data"


def get_spark() -> SparkSession:
    return SparkSession.builder.getOrCreate()


def _join(data_dir: str, filename: str) -> str:
    base = data_dir.rstrip("/")
    return f"{base}/{filename}"


def ingest_all(
    spark: SparkSession,
    data_dir: str = DEFAULT_DATA_DIR,
) -> list[dict]:
    """
    Ingest customers → orders → products. Stop on first error.
    Returns metadata dicts (table, source_path, row_count, ingest_ts).
    """
    jobs = [
        (
            "customers",
            _customers.ingest_customers,
            _join(data_dir, "customers.csv"),
            "bronze.customers",
        ),
        (
            "orders",
            _orders.ingest_orders,
            _join(data_dir, "orders.csv"),
            "bronze.orders",
        ),
        (
            "products",
            _products.ingest_products,
            _join(data_dir, "products.csv"),
            "bronze.products",
        ),
    ]

    results: list[dict] = []
    for name, fn, path, table in jobs:
        print(f"[Bronze] Starting {name} from {path} → {table}")
        try:
            meta = fn(spark, path, table)
        except Exception as exc:
            print(f"[Bronze] FAILED on {name}: {exc}")
            raise
        results.append(meta)

    print("=== Bronze ingest_all summary ===")
    for meta in results:
        print(
            f"  {meta['table']}: rows={meta['row_count']} "
            f"ts={meta['ingest_ts']} source={meta['source_path']}"
        )
    return results


def main() -> None:
    spark = get_spark()
    try:
        dbutils.widgets.text(  # type: ignore[name-defined]
            "data_dir",
            DEFAULT_DATA_DIR,
            "CSV directory on DBFS",
        )
        data_dir = dbutils.widgets.get("data_dir")  # type: ignore[name-defined]
    except Exception:
        data_dir = DEFAULT_DATA_DIR

    ingest_all(spark, data_dir)


if __name__ == "__main__":
    main()
