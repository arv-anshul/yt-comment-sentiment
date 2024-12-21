from datetime import datetime
from typing import Literal

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, NonNegativeInt, PositiveInt

_BASE_URL = "https://www.googleapis.com/youtube/v3"

router = APIRouter(
    prefix="/youtube",
    tags=["youtube"],
)


async def get_youtube_client(
    x_api_key: str = Header(),
):
    params = {
        "key": x_api_key,
    }
    client = httpx.AsyncClient(
        base_url=_BASE_URL,
        params=params,
        timeout=10,
    )
    yield client
    await client.aclose()


def check_youtube_client_response(res: httpx.Response):
    if res.status_code == 200:
        return
    raise HTTPException(res.status_code, res.json()["error"]["message"])


class YTVideoDetails(BaseModel):
    id: str
    title: str
    description: str
    channelTitle: str
    publishedAt: datetime
    duration: str
    viewCount: NonNegativeInt
    likeCount: NonNegativeInt
    commentCount: NonNegativeInt


@router.get("/video-details", response_model=YTVideoDetails)
async def fetch_youtube_video_details(
    video_id: str,
    client: httpx.AsyncClient = Depends(get_youtube_client),
):
    """
    Fetches basic details of a YouTube video using the YouTube Data API v3.
    """
    params = {
        "part": "snippet,contentDetails,statistics",
        "id": video_id,
    }

    response = await client.get("/videos", params=params)
    check_youtube_client_response(response)

    data = response.json()
    if not ("items" in data and len(data["items"])):
        raise HTTPException(400, "No video found for the given ID.")
    video_details = data["items"][0]
    return {
        "id": video_id,
        "title": video_details["snippet"]["title"],
        "description": video_details["snippet"]["description"],
        "channelTitle": video_details["snippet"]["channelTitle"],
        "publishedAt": video_details["snippet"]["publishedAt"],
        "duration": video_details["contentDetails"]["duration"],
        "viewCount": video_details["statistics"].get("viewCount", 0),
        "likeCount": video_details["statistics"].get("likeCount", 0),
        "commentCount": video_details["statistics"].get("commentCount", 0),
    }


class CommentDetails(BaseModel):
    authorDisplayName: str
    authorProfileImageUrl: str
    textDisplay: str
    likeCount: NonNegativeInt
    publishedAt: datetime


class VideoCommentsResponse(BaseModel):
    video_id: str
    totalComments: PositiveInt
    comments: list[CommentDetails]


@router.get("/video-comments", response_model=VideoCommentsResponse)
async def fetch_youtube_video_comments(
    video_id: str,
    max_comments: int = Query(100, ge=50, le=3000),
    order: Literal["time", "relevance"] = "relevance",
    client: httpx.AsyncClient = Depends(get_youtube_client),
):
    """
    Fetches a large number of comments for a YouTube video using the YouTube Data API v3.
    """
    params = {
        "part": "snippet",
        "videoId": video_id,
        "order": order,
        "maxResults": min(100, max_comments),  # Maximum allowed by the API per request
        "textFormat": "plainText",
    }

    comments = []
    next_page_token = None

    while len(comments) < max_comments:
        if next_page_token:
            params["pageToken"] = next_page_token

        response = await client.get("/commentThreads", params=params)
        check_youtube_client_response(response)

        data = response.json()

        if "items" not in data or not data["items"]:
            break

        for item in data["items"]:
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            _o = {
                "authorDisplayName": snippet["authorDisplayName"],
                "authorProfileImageUrl": snippet["authorProfileImageUrl"],
                "textDisplay": snippet["textDisplay"],
                "likeCount": snippet.get("likeCount", 0),
                "publishedAt": snippet["publishedAt"],
            }
            comments.append(_o)

            if len(comments) >= max_comments:
                break

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    if not comments:
        raise HTTPException(400, "No comments found for the given video ID.")

    return {
        "video_id": video_id,
        "totalComments": len(comments),
        "comments": comments,
    }
