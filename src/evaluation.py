from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import joblib
import mlflow
import mlflow.sklearn
import polars as pl
import seaborn as sns
from loguru import logger
from matplotlib import pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix

from src.params import params

if TYPE_CHECKING:
    import numpy as np


def evaluate(
    model,
    x_test_vec: np.ndarray,
    y_test: np.ndarray,
) -> tuple[dict, np.ndarray]:
    y_pred = model.predict(x_test_vec)

    logger.debug("Calculating classification_report...")
    report: dict = classification_report(
        y_test,
        y_pred,
        output_dict=True,
        target_names=params.dataset.target_labels,
    )  # type: ignore
    logger.debug("Calculating confusion_matrix...")
    cm = confusion_matrix(y_test, y_pred)

    return report, cm


def log_confusion_matrix(
    cm: np.ndarray,
    dataset_type: Literal["train", "test"],
) -> None:
    """Log confusion matrix as an artifact."""
    logger.info("Logging confusion_matrix as an artifact...")

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        xticklabels=params.dataset.target_labels,
        yticklabels=params.dataset.target_labels,
    )
    plt.title(f"Confusion Matrix for {dataset_type} dataset")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    # Save confusion matrix plot as a file and log it to MLflow
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_fp = Path(tmp_dir) / "confusion_matrix.png"
        plt.savefig(tmp_fp)
        mlflow.log_artifact(tmp_fp.as_posix())

    plt.close()

    # FIXME: log confusion metrics values separately
    # tn, fp, fn, tp = cm.ravel()
    # mlflow.log_metrics({"TN": tn, "FP": fp, "FN": fn, "TP": tp})


def log_classification_report(
    report: dict,
    dataset_type: Literal["train", "test"],
) -> None:
    logger.info("Logging classification_report...")
    for label, metrics in report.items():
        if label in params.dataset.target_labels:
            mlflow.log_metrics(
                {
                    f"{dataset_type}_{label}_precision": metrics["precision"],
                    f"{dataset_type}_{label}_recall": metrics["recall"],
                    f"{dataset_type}_{label}_f1-score": metrics["f1-score"],
                },
            )
    mlflow.log_metric("test_accuracy", report["accuracy"])


def log_models(model) -> None:
    """Log ML model with vectorizer as artifacts."""
    logger.debug("Logging model with mlflow")
    # TODO: learn and implement/use infer_signature() function
    mlflow.sklearn.log_model(model, "model")
    mlflow.set_tag("model_name", params.building.model.name)
    mlflow.log_params(params.building.model.params)

    logger.debug("Logging vectorizer as an artifact")
    mlflow.log_artifact(params.building.vectorizer.path)
    mlflow.set_tag("vectorizer_name", params.building.vectorizer.name)


def store_mllfow_run_info(run: mlflow.ActiveRun) -> None:
    info = {
        "model_path": "model",
        "run_id": run.info.run_id,
    }

    path = "mlflow_run_info.json"
    logger.info("Dumping last mlflow run info at {!r}", path)
    with Path(path).open("w") as f:
        json.dump(info, f, indent=2)


def setup_mlflow() -> None:
    logger.info("Setting up mlflow configs...")
    tracking_uri: str = params.mlflow.tracking_uri
    # Infer path if tracking_uri is not a url
    if not tracking_uri.startswith("http"):
        tracking_uri = Path(tracking_uri).resolve().absolute().as_uri()
    logger.info("Mlflow tracking URI is {!r}", tracking_uri)
    mlflow.set_tracking_uri(tracking_uri)

    logger.info(
        "Following run comes under experiment {!r}.",
        params.mlflow.experiment_name,
    )
    mlflow.set_experiment(params.mlflow.experiment_name)


def main() -> None:
    logger.critical("Model evaluation starts...")
    start_time = time.perf_counter()

    logger.debug("Loading vectorizer, model and test_df")
    vectorizer = joblib.load(params.building.vectorizer.path)
    model = joblib.load(params.building.model.path)

    test_df = pl.read_parquet(params.ingestion.processed_test_path)
    logger.debug("Transforming x_test data with vectorizer")
    x_test_vec = vectorizer.transform(test_df["text"].to_numpy()).toarray()  # type: ignore
    y_test = test_df["target"].to_numpy()

    report, cm = evaluate(model, x_test_vec, y_test)

    setup_mlflow()
    with mlflow.start_run() as run:
        logger.critical("Started new mlflow run: {!r}", run.info.run_id)
        log_confusion_matrix(cm, "test")
        log_classification_report(report, "test")
        log_models(model)
        store_mllfow_run_info(run)

    logger.critical(
        "Model evaluation ends in {:.3f} seconds.",
        time.perf_counter() - start_time,
    )


if __name__ == "__main__":
    main()
