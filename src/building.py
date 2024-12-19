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

from src.params import params


def build_pipeline() -> Pipeline:
    # import vectorizer class
    vec_params = params.building.vectorizer
    module = importlib.import_module(vec_params.module)
    _params: dict[str, Any] = vec_params.params.copy()
    ngram_range = tuple(_params.pop("ngram_range", [1, 1]))
    vectorizer = getattr(module, vec_params.name)(
        ngram_range=ngram_range,
        **_params,
    )
    logger.debug("{} imported from {} module.", vec_params.name, vec_params.module)

    # import model class
    model_params = params.building.model
    module = importlib.import_module(model_params.module)
    model = getattr(module, model_params.name)(**model_params.params)
    logger.debug("{} imported from {} module.", model_params.name, model_params.module)

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
    model_params = params.building.model

    # train model
    pipeline.fit(x_train, y_train)
    logger.debug("Pipeline is trained on x_train data.")

    # store model
    _model_path = Path(model_params.path)
    _model_path.parent.mkdir(parents=True, exist_ok=True)
    with _model_path.open("wb") as f:
        cloudpickle.dump(pipeline, f)
    logger.debug("Pipeline is stored at {!r}.", model_params.path)


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
