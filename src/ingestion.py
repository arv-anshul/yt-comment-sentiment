import time
from functools import cache
from pathlib import Path

import nltk
import polars as pl
from loguru import logger
from nltk.corpus import stopwords as nltk_stopwords

from ml.params import params

# download nltk essentials
nltk.download("punkt")
nltk.download("stopwords")

_lemmatizer = nltk.WordNetLemmatizer()


@cache
def _load_stopwords() -> set[str]:
    logger.debug("loading stopwords...")
    # infered from EDA
    # TODO: read from json file
    skip_words = {"not", "but", "however", "no", "yet"}
    return set(nltk_stopwords.words("english")) - skip_words


def preprocess_text(text: str):
    word_tokens = nltk.word_tokenize(text)

    # infered from EDA
    stop_words = _load_stopwords()
    word_tokens = [word for word in word_tokens if word not in stop_words]

    word_tokens = [_lemmatizer.lemmatize(word) for word in word_tokens]

    text = " ".join(word_tokens)
    return text


def ingest_data() -> pl.LazyFrame:
    # load data using dataset url
    url = params.dataset.url
    logger.debug("Ingesting data from {!r}.", url)
    df = pl.scan_csv(url) if url.endswith(".csv") else pl.scan_parquet(url)

    # apply preprocessing steps
    logger.debug("Applying preprocessing steps on dataset.")
    df = (
        df.rename(params.dataset.rename_columns)
        .with_columns(
            pl.col("text")
            .str.to_lowercase()
            .str.strip_chars()
            .str.replace_all(r"\n", " ")
            .str.replace_all(r"[^A-Za-z0-9\s!?.,]", ""),
            # .map_elements(preprocess_text, pl.String)
        )
        .filter(
            pl.col("text").is_in(["", " "]).not_(),
        )
        .drop_nulls()
    )

    return df


def split_into_train_test(_df: pl.LazyFrame, /) -> tuple[pl.DataFrame, pl.DataFrame]:
    logger.debug("Spliting preprocessed data into train and test dataset.")
    df = _df.collect().with_columns(
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
