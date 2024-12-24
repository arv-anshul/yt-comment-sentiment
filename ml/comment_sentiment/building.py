from __future__ import annotations

import importlib
import time
from pathlib import Path
from typing import Any

import cloudpickle
import polars as pl
from loguru import logger
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from ml.params import params


def build_pipeline() -> Pipeline:
    # import vectorizer class
    module = importlib.import_module(params.vectorizer.module)
    _params: dict[str, Any] = params.vectorizer.params.copy()
    ngram_range = tuple(_params.pop("ngram_range", [1, 1]))
    vectorizer = getattr(module, params.vectorizer.name)(
        ngram_range=ngram_range,
        **_params,
    )
    logger.debug(
        "{} imported from {} module.",
        params.vectorizer.name,
        params.vectorizer.module,
    )

    # import model class
    module = importlib.import_module(params.model.module)
    model = getattr(module, params.model.name)(**params.model.params)
    logger.debug("{} imported from {} module.", params.model.name, params.model.module)

    # convert sparse output of vectorizer into dense array
    to_dense = FunctionTransformer(
        lambda x: x.toarray(),
        validate=True,
        accept_sparse=True,
    )

    # create pipeline object
    pipeline = Pipeline(
        steps=[
            ("vectorizer", vectorizer),
            ("to_dense", to_dense),
            ("model", model),
        ],
    )
    return pipeline


def train_pipeline(
    pipeline: Pipeline,
    x_train: pl.Series,
    y_train: pl.Series,
) -> None:
    # train model
    pipeline.fit(x_train, y_train)
    logger.debug("Pipeline is trained on x_train data.")

    # store model
    _model_path = Path(params.pipeline.path)
    _model_path.parent.mkdir(parents=True, exist_ok=True)
    with _model_path.open("wb") as f:
        cloudpickle.dump(pipeline, f)
    logger.debug("Pipeline is stored at {!r}.", params.pipeline.path)


def main() -> None:
    logger.info("Initiating model building stage...")
    start_time = time.perf_counter()

    if not Path(params.ingestion.processed_train_path).exists():
        msg = f"{params.ingestion.processed_train_path} path not exists."
        raise FileNotFoundError(msg)
    train_df = pl.read_parquet(params.ingestion.processed_train_path)
    logger.debug(
        "Load train data from {!r} file.",
        params.ingestion.processed_train_path,
    )

    pipeline = build_pipeline()
    train_pipeline(pipeline, train_df["text"], train_df["target"])

    logger.info(
        "Model building stage ends after {:.3f} seconds.",
        time.perf_counter() - start_time,
    )


if __name__ == "__main__":
    main()
