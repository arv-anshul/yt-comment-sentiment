from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import cloudpickle
import mlflow
import mlflow.sklearn
import polars as pl
import seaborn as sns
from loguru import logger
from matplotlib import pyplot as plt
from mlflow.environment_variables import MLFLOW_TRACKING_URI
from sklearn.metrics import classification_report, confusion_matrix

from ml.params import params

if TYPE_CHECKING:
    import numpy as np
    from sklearn.pipeline import Pipeline


def evaluate(
    model: Pipeline,
    x_test: pl.Series,
    y_test: pl.Series,
) -> tuple[dict, np.ndarray]:
    y_pred = model.predict(x_test)

    logger.debug("Calculating classification_report...")
    report: dict = classification_report(
        y_test,
        y_pred,
        output_dict=True,
        target_names=params.dataset.target_labels.values(),
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

    labels = params.dataset.target_labels.values()

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        xticklabels=labels,
        yticklabels=labels,
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
        if label in params.dataset.target_labels.values():
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
    mlflow.set_tag("model_name", params.model.name)
    mlflow.log_params(params.model.params)

    logger.debug("Logging vectorizer name and params")
    mlflow.log_params(params.vectorizer.params)
    mlflow.set_tag("vectorizer_name", params.vectorizer.name)


def store_mllfow_run_info(run: mlflow.ActiveRun) -> None:
    info = {
        "model_path": "model",
        "run_id": run.info.run_id,
    }

    path = "mlflow_run_info.json"
    logger.info("Dumping last mlflow run info at {!r}", path)
    with Path(path).open("w") as f:
        json.dump(info, f, indent=2)


def main() -> None:
    import os
    import time

    import dagshub

    logger.critical("Model evaluation starts...")

    if _dagshub_init_url := os.getenv("DAGSHUB_INIT_URL"):
        logger.critical("Initialize DagsHub...")
        dagshub.init(url=_dagshub_init_url, mlflow=True)  # type: ignore
    else:
        logger.critical("Skipping DagsHub initialization assuming a local experiment.")
        MLFLOW_TRACKING_URI.set(Path("./mlruns").absolute().resolve().as_uri())

    start_time = time.perf_counter()

    logger.debug("Loading pipeline from {!r}.", params.pipeline.path)
    with Path(params.pipeline.path).open("rb") as f:
        pipeline = cloudpickle.load(f)

    logger.debug(
        "Loading test data from {!r} file.",
        params.ingestion.processed_test_path,
    )
    test_df = pl.read_parquet(params.ingestion.processed_test_path)

    report, cm = evaluate(pipeline, test_df["text"], test_df["target"])

    logger.critical("Mlflow tracking URI is {!r}", MLFLOW_TRACKING_URI.get())
    with mlflow.start_run() as run:
        logger.critical("Started new mlflow run: {!r}", run.info.run_id)
        log_confusion_matrix(cm, "test")
        log_classification_report(report, "test")
        log_models(pipeline)
        store_mllfow_run_info(run)

    logger.critical(
        "Model evaluation ends in {:.3f} seconds.",
        time.perf_counter() - start_time,
    )


if __name__ == "__main__":
    main()
