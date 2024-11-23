from __future__ import annotations

import importlib
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import joblib
import polars as pl
from loguru import logger

from src.params import params

if TYPE_CHECKING:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer


def build_vectorizer(x_train: pl.Series) -> np.ndarray:
    vec_params = params.building.vectorizer

    # import vectorizer class
    module = importlib.import_module(vec_params.module)
    _params: dict[str, Any] = vec_params.params.copy()
    ngram_range = tuple(_params.pop("ngram_range", [1, 1]))
    vectorizer: TfidfVectorizer = getattr(module, vec_params.name)(
        ngram_range=ngram_range,
        **_params,
    )
    logger.debug("{} imported from {} module.", vec_params.name, vec_params.module)

    # train vectorizer
    # transform x_train data
    x_train_vec = vectorizer.fit_transform(x_train).toarray()  # type: ignore
    logger.info("Vectorizer applied on x_train ({})", x_train.shape)

    # store transformed x_train_vec (for evaluation)
    Path(params.evaluation.train_vec_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(x_train_vec, params.evaluation.train_vec_path)
    logger.debug("Stored x_train_vec at {!r}.", params.evaluation.train_vec_path)

    # store trained vectorizer object
    Path(vec_params.path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, vec_params.path)
    logger.debug("Vectorizer stored at {!r}.", vec_params.path)

    return x_train_vec


def build_model(x_train_vec: np.ndarray, y_train: np.ndarray) -> None:
    model_params = params.building.model

    # import model class
    module = importlib.import_module(model_params.module)
    model = getattr(module, model_params.name)(**model_params.params)
    logger.debug("{} imported from {} module.", model_params.name, model_params.module)

    # train model
    model.fit(x_train_vec, y_train)
    logger.debug("{!r} model is trained on vectorized data.", model_params.name)

    # store model
    Path(model_params.path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_params.path)
    logger.debug("Model is stored at {!r}.", model_params.path)


def main() -> None:
    logger.info("Initiating model building...")
    start_time = time.perf_counter()

    if not Path(params.ingestion.processed_train_path).exists():
        msg = f"{params.ingestion.processed_train_path} path not exists."
        raise FileNotFoundError(msg)
    train_df = pl.read_parquet(params.ingestion.processed_train_path)

    x_train_vec = build_vectorizer(train_df["text"])
    build_model(x_train_vec, train_df["target"].to_numpy())

    logger.info(
        "Mdoel building ends after {:.3f} seconds.",
        time.perf_counter() - start_time,
    )


if __name__ == "__main__":
    main()
