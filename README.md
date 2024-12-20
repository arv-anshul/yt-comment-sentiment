# YouTube Comment Sentiment

An end-to-end project to predict the sentiment of YouTube video comments using Machine Learning.

## Overview

This project focuses on building a sentiment analysis system for YouTube comments, complete with a FastAPI-based
inference endpoint and insights-providing API endpoints. The development process included robust experimentation,
tracking, and pipeline reproduction (using **MLFlow** and **DVC**).

![diagram](assets/diagram.png)

### Key Features

- **Inference Endpoint:** Built using the FastAPI framework to classify sentiment of comments.
- **Insights Endpoints:** Additional APIs to provide analytics around comment sentiments.
- **Experiment Tracking:** Leveraged MLFlow for tracking experiments.
- **Pipeline Reproduction:** Utilized DVC (Data Version Control) for reproducibility.
- **Text Vectorization:** Used `TfidfVectorizer` for transforming text data into feature vectors.
- **Model Selection:** Experimented with various models and selected `HistGradientBoostingClassifier` as the
  best-performing classifier.

## Experimentation

The experimentation phase focused on optimizing hyperparameters for the `TfidfVectorizer` and
`HistGradientBoostingClassifier` model. Below is a screenshot showcasing how different hyperparameter combinations
impacted accuracy:

![Experiment Results](./assets/TFIDF-HistGB.png)

## Tech Stack

|                        Tech | Stack                                                                                                                                                                                                                                                                                                                                                                                                      |
| --------------------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|    **Programming Language** | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)                                                                                                                                                                                                                                                                                                                            |
|           **Data Handling** | ![Polars](https://img.shields.io/badge/Polars-CD792C?logo=polars&logoColor=fff)                                                                                                                                                                                                                                                                                                                            |
|    **Frameworks and Tools** | ![MLflow](https://img.shields.io/badge/MLflow-0194E2?logo=mlflow&logoColor=fff) ![DVC](https://img.shields.io/badge/DVC-13ADC7?logo=dvc&logoColor=fff) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=fff)                                                                                                                                                                  |
| **Machine Learning Models** | ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=fff) ![NLTK](https://img.shields.io/badge/NLTK-3776AB?logo=python&logoColor=fff)                                                                                                                                                                                                                              |
|       **Project Dev Tools** | ![uv](https://img.shields.io/badge/uv-DE5FE9?logo=uv&logoColor=fff) ![pre-commit](https://img.shields.io/badge/pre--commit-FAB040?logo=precommit&logoColor=fff) ![Ruff](https://img.shields.io/badge/Ruff-D7FF64?logo=ruff&logoColor=fff) ![Zed](https://img.shields.io/badge/Zed-084CCF?logo=zedindustries&logoColor=fff) ![Loguru](https://img.shields.io/badge/Loguru-3776AB?logo=python&logoColor=fff) |

## More to do!

1. [x] Merge **both classifier model and vectorizer model** which reduce the complexity of loading them using using
       `MLFLOW_RUN_ID` in [`app.py`](backend/app.py).
2. [ ] After completing previous step, load model using `MLFLOW_MODEL_URI` env instead of `MLFLOW_RUN_ID` env.
3. [ ] ⚠️ Try to use `MLproject` file to run ML Pipeline steps instead of [`dvc.yaml`](dvc.yaml) file. _(Only if
       Possible)_
   - [ ] Also investigate the use `dvc` here and try to know WHY, WHAT and HOW (part of it).
4. [ ] Know the clear distinction and involvement between the source code of ML Pipeline, Backend.

---

> \[!IMPORTANT\]
>
> Feel free to explore and contribute!
