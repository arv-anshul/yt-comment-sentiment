import time
import urllib.parse
from collections.abc import Callable
from datetime import datetime
from io import BytesIO
from typing import Literal

import mlflow
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from matplotlib import pyplot as plt
from pydantic import BaseModel
from wordcloud import WordCloud

from backend.utils import getenv, load_model_and_vectorizer
from src.ingestion import preprocess_text
from src.params import params

MLFLOW_MODEL_NAME = getenv("MLFLOW_MODEL_NAME")
MLFLOW_MODEL_VERSION = getenv("MLFLOW_MODEL_VERSION")
MLFLOW_RUN_ID = getenv("MLFLOW_RUN_ID")

SentimentType = Literal["positive", "neutral", "negative"]

mlflow.set_tracking_uri(params.mlflow.tracking_uri)
model, vectorizer = load_model_and_vectorizer(run_id=MLFLOW_RUN_ID)

app = FastAPI(
    title="YouTube Comment Sentiment Analyser - API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    return response


@app.get("/")
async def root() -> dict:
    return {
        "author": "https://github.com/arv-anshul",
    }


@app.get("/validate-yt-url")
async def verify_youtube_url(url: str):
    parsed = urllib.parse.urlparse(url)

    video_id: str | None = None
    match parsed.netloc, parsed.path:
        case "youtube.com" | "www.youtube.com", "/watch":
            id_list = urllib.parse.parse_qs(parsed.query).get("v")
            if not id_list:
                raise HTTPException(422, "validation error, bad youtube video url.")
            video_id = id_list[0]
        case "youtu.be", _id:
            video_id = _id.strip("/")
        case "", path if path.startswith("youtu.be/"):
            video_id = path.strip("youtu.be/")
        case _:
            content = {
                "error": "validation error",
                "detail": "This is not a valid youtube video url.",
                "url": url,
            }
            return JSONResponse(content, 422)

    return {
        "message": "validation passed",
        "url": url,
        "video_id": video_id,
    }


class CommentInput(BaseModel):
    comment: str
    timestamp: datetime | None = None


class CommentOutput(CommentInput):
    sentiment: int


@app.post("/predict")
async def predict(comments: list[CommentInput]) -> list[CommentOutput]:
    if not comments:
        raise HTTPException(400, "No comments provided.")

    comments_trf = vectorizer.transform([i.comment for i in comments]).toarray()
    sentiments = model.predict(comments_trf)
    return [
        CommentOutput(comment=c.comment, timestamp=c.timestamp, sentiment=s)
        for c, s in zip(comments, sentiments)
    ]


class SentimentCountInput(BaseModel):
    positive: int
    neutral: int
    negative: int


@app.post("/sentiment-count-plot")
async def sentiment_count_plot(
    body: SentimentCountInput,
    text_color: Literal["w", "k"] = "k",
):
    data = body.model_dump()

    plt.figure(figsize=(6, 6))
    plt.pie(
        list(data.values()),
        labels=[i.title() for i in data],
        colors=["#36A2EB", "#C9CBCF", "#FF6384"],
        autopct="%1.1f%%",
        startangle=140,
        textprops={"color": text_color},
    )
    # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.axis("equal")

    # Store image into BytesIO object and return
    io = BytesIO()
    plt.savefig(io, format="PNG", transparent=True)
    io.seek(0)
    plt.close()

    return StreamingResponse(io, media_type="image/png")


@app.post("/comments-wordcloud")
async def comments_wordcloud(
    comments: list[str],
    sentiment_type: SentimentType | None = None,
    background_color: Literal["white", "black"] = "black",
):
    processed_comments = " ".join(preprocess_text(txt) for txt in comments)
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color=background_color,
        colormap="Blues",
        collocations=False,
    ).generate(processed_comments)

    # Save the word cloud to a BytesIO object
    io = BytesIO()
    wordcloud.to_image().save(io, format="PNG")
    io.seek(0)

    return StreamingResponse(io, media_type="image/png")
