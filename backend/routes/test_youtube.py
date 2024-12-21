import secrets

from fastapi.testclient import TestClient

from ..app import app
from ..utils import getenv

_YOUTUBE_API_KEY = getenv("YOUTUBE_API_KEY")
_VIDEO_ID = "eCjuoqUy8Is"  # A fixed video id for testing

client = TestClient(app, headers={"x-api-key": _YOUTUBE_API_KEY})


def test_fetch_youtube_video_details():
    params = {"video_id": _VIDEO_ID}
    response = client.get("/youtube/video-details", params=params)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == _VIDEO_ID
    assert (
        data["title"]
        == "How to build a ML project using MLOps | MLOps in Hindi | CampusX"
    )
    assert data["channelTitle"] == "CampusX"
    assert "description" in data
    assert "publishedAt" in data
    assert "duration" in data
    assert "viewCount" in data
    assert "likeCount" in data
    assert "commentCount" in data


def test_fetch_youtube_video_comments():
    params = {
        "video_id": _VIDEO_ID,
        "max_comments": 51 + secrets.randbelow(48),  # range(51, 100)
    }
    response = client.get("/youtube/video-comments", params=params)
    assert response.status_code == 200

    data = response.json()
    assert data["video_id"] == _VIDEO_ID
    assert data["totalComments"] == params["max_comments"]
    assert len(data["comments"]) == params["max_comments"]


def test_video_details_invalid_key():
    params = {"video_id": _VIDEO_ID}
    headers = {"x-api-key": "invalid_api_key"}
    response = client.get("/youtube/video-details", params=params, headers=headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "API key not valid. Please pass a valid API key.",
    }


def test_video_comments_invalid_key():
    params = {"video_id": _VIDEO_ID}
    headers = {"x-api-key": "invalid_api_key"}
    response = client.get("/youtube/video-comments", params=params, headers=headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "API key not valid. Please pass a valid API key.",
    }
