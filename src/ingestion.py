import time
from pathlib import Path

import polars as pl
from loguru import logger

from src.params import params


def preprocess_comments(expr: pl.Expr) -> pl.Expr:
    logger.debug("Applying preprocessing steps on dataset.")
    return (
        expr.str.to_lowercase()
        .str.strip_chars()
        .str.replace_all(r"\n", " ", literal=True)
        .str.replace_all(r"[^A-Za-z0-9\s!?.,]", "")
    )


def ingest_data() -> pl.DataFrame:
    # load data using dataset url
    url = params.dataset.url
    logger.debug("Ingesting data from {!r}.", url)
    df = pl.read_csv(url) if url.endswith(".csv") else pl.read_parquet(url)
    logger.info("Ingested data has {} rows.", df.height)

    df = (
        df.rename(params.dataset.rename_columns)
        .with_columns(
            pl.col("text").pipe(preprocess_comments),
        )
        .filter(
            pl.col("text").is_in(["", " "]).not_(),
            pl.col("text").str.split(" ").list.len().gt(3),
        )
        .drop_nulls()
    )

    logger.info("After preprocessing we have only {} rows.", df.height)

    return df


def split_into_train_test(_df: pl.DataFrame, /) -> tuple[pl.DataFrame, pl.DataFrame]:
    logger.debug("Spliting preprocessed data into train and test dataset.")
    df = _df.with_columns(
        split_on=pl.int_range(pl.len(), dtype=pl.UInt32),
    )

    train_df = df.sample(fraction=params.dataset.train_size, seed=42, shuffle=True)
    test_df = df.filter(pl.col("split_on").is_in(train_df["split_on"]).not_())

    return train_df, test_df


def store_train_test_data(_df: tuple[pl.DataFrame, pl.DataFrame], /) -> None:
    """Store data in parquet format."""
    Path(params.ingestion.processed_train_path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    train_path = params.ingestion.processed_train_path
    logger.debug("Storing preprocessed train data at {}", train_path)
    _df[0].write_parquet(train_path)

    test_path = params.ingestion.processed_test_path
    logger.debug("Storing preprocessed train data at {}", test_path)
    _df[1].write_parquet(test_path)


def main() -> None:
    logger.info("Initiating data ingestion...")
    start_time = time.perf_counter()

    ingested_data = ingest_data()
    train_df, test_df = split_into_train_test(ingested_data)
    store_train_test_data((train_df, test_df))

    logger.info(
        "Data ingestion ends after {:.3f} seconds.",
        time.perf_counter() - start_time,
    )


if __name__ == "__main__":
    main()
