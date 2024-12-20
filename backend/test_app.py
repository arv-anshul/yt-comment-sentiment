"""Tests for backend APIs made with FastAPI"""

import pytest
from fastapi.testclient import TestClient

from .app import app

client = TestClient(app)


@pytest.fixture
def test_comments():
    return [
        {"text": "This is amazing!"},
        {"text": "Could be better."},
        {"text": "I loved the video."},
        {"text": "Not my cup of tea."},
        {"text": "Absolutely fantastic!"},
    ]


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"author": "https://github.com/arv-anshul"}


@pytest.mark.parametrize(
    ("url", "expected_status", "expected_video_id"),
    [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", 200, "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", 200, "dQw4w9WgXcQ"),
        ("invalid_url", 422, None),
    ],
)
def test_validate_yt_url(url: str, expected_status: int, expected_video_id: str):
    response = client.get(f"/validate-yt-url?url={url}")
    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json()["video_id"] == expected_video_id


def test_predict_empty_comments():
    response = client.post("/predict", json=[])
    assert response.status_code == 400
    assert response.json()["detail"] == "No comments provided."


def test_predict_valid_comments(test_comments):
    response = client.post("/predict", json=test_comments)
    assert response.status_code == 200
    json_data = response.json()
    assert "comments" in json_data
    assert "sentiment_count" in json_data
    assert len(json_data["comments"]) == len(test_comments)


def test_sentiment_count_plot():
    body = {"positive": 5, "neutral": 3, "negative": 2}
    response = client.post("/sentiment-count-plot", json=body)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_comments_wordcloud(test_comments):
    comments = [i["text"] for i in test_comments]
    response = client.post("/comments-wordcloud", json=comments)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
