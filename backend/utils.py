import os
import tempfile
from functools import cache
from pathlib import Path
from typing import Any

import joblib
import mlflow
import mlflow.sklearn
from src.params import params


def getenv(name: str, default: Any = None) -> str:
    env = os.getenv(name, default)
    if env is None:
        raise ValueError(f"env {name!r} not specified.")
    return env


@cache
def load_model_and_vectorizer(run_id: str) -> tuple[Any, Any]:
    # model_uri = f"models:/{MLFLOW_MODEL_NAME}/{MLFLOW_MODEL_VERSION}"
    model_uri = f"runs:/{run_id}/model"
    model = mlflow.sklearn.load_model(model_uri)

    client = mlflow.MlflowClient()
    # First download vectorizer in local directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = client.download_artifacts(
            run_id,
            Path(params.building.vectorizer.path).name,
            tmp_dir,
        )
        vectorizer = joblib.load(path)
    return model, vectorizer
