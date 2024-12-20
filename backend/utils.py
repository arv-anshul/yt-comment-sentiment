from __future__ import annotations

import os
from functools import cache
from typing import TYPE_CHECKING, Any

import mlflow.sklearn

if TYPE_CHECKING:
    from sklearn.pipeline import Pipeline


def getenv(name: str, default: Any = None) -> str:
    env = os.getenv(name, default)
    if env is None:
        raise ValueError(f"env {name!r} not specified.")
    return env


@cache
def load_model(model_uri: str) -> Pipeline:
    model = mlflow.sklearn.load_model(model_uri)
    if model is None:
        raise FileNotFoundError("error while importing model from its URI")
    return model
