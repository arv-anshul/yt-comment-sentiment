/**
 *  Fetches comments from a YouTube video using videoId
 */
export async function getVideoComments(
  videoId,
  maxComments = 100,
  order = "relevance"
) {
  try {
    const response = await fetch(
      `/api/youtube/video-comments?video_id=${videoId}&max_comments=${maxComments}&order=${order}`,
      {
        headers: {
          "X-API-KEY": import.meta.env.VITE_YOUTUBE_API_KEY,
        },
      }
    );
    const data = await response.json();

    if (!response.ok) {
      throw new Error(JSON.stringify(data));
    }

    return data;
  } catch (e) {
    console.error(e);
  }
}

/**
 *  Fetches sentiment prediction of comments
 */
export async function predictCommentsSentiments(comments) {
  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(comments),
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(JSON.stringify(data));
    }

    return data;
  } catch (e) {
    console.error(e);
  }
}

/**
 *  Merges comments with corresponding sentiments.
 */
export function mergeCommentsAndSentiments(rawComments, commentsWithSentiment) {
  console.log(rawComments.length, rawComments);
  console.log(commentsWithSentiment.length, commentsWithSentiment);
  const merged = rawComments.map((comment, index) => ({
    ...comment,
    sentiment: commentsWithSentiment.comments[index].sentiment,
  }));
  return merged;
}
