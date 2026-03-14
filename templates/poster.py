import os
import requests
import logging

logger = logging.getLogger(__name__)

# Meta (Instagram + Facebook)
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID", "")

# YouTube
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
YOUTUBE_CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "")


def post_to_instagram(image_url: str, caption: str) -> dict:
    """Post image to Instagram via Meta Graph API."""
    if not META_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        logger.warning("Instagram credentials not set — skipping")
        return {"platform": "instagram", "status": "skipped", "reason": "credentials not set"}

    try:
        # Step 1: Create media container
        container_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
        container_resp = requests.post(container_url, data={
            "image_url": image_url,
            "caption": caption,
            "access_token": META_ACCESS_TOKEN
        }, timeout=30)
        container_resp.raise_for_status()
        container_id = container_resp.json().get("id")

        # Step 2: Publish the container
        publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        publish_resp = requests.post(publish_url, data={
            "creation_id": container_id,
            "access_token": META_ACCESS_TOKEN
        }, timeout=30)
        publish_resp.raise_for_status()
        post_id = publish_resp.json().get("id")

        logger.info(f"✅ Posted to Instagram: {post_id}")
        return {"platform": "instagram", "status": "success", "post_id": post_id}
    except Exception as e:
        logger.error(f"Instagram post failed: {e}")
        return {"platform": "instagram", "status": "failed", "error": str(e)}


def post_to_facebook(image_url: str, caption: str) -> dict:
    """Post image to Facebook Page via Graph API."""
    if not META_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
        logger.warning("Facebook credentials not set — skipping")
        return {"platform": "facebook", "status": "skipped", "reason": "credentials not set"}

    try:
        url = f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/photos"
        resp = requests.post(url, data={
            "url": image_url,
            "caption": caption,
            "access_token": META_ACCESS_TOKEN
        }, timeout=30)
        resp.raise_for_status()
        post_id = resp.json().get("id")

        logger.info(f"✅ Posted to Facebook: {post_id}")
        return {"platform": "facebook", "status": "success", "post_id": post_id}
    except Exception as e:
        logger.error(f"Facebook post failed: {e}")
        return {"platform": "facebook", "status": "failed", "error": str(e)}


def post_to_youtube(image_url: str, concept: dict) -> dict:
    """
    YouTube Shorts requires a video file. 
    For meme images, we note this as pending — 
    a future upgrade can convert image→short video via ffmpeg.
    """
    logger.info("YouTube Shorts posting: requires video conversion (planned upgrade)")
    return {
        "platform": "youtube",
        "status": "pending",
        "reason": "Image-to-Shorts conversion coming in next phase"
    }


def post_to_all_platforms(image_url: str, concept: dict) -> list:
    """Post to all platforms and return results."""
    caption = concept.get("platform_caption", concept.get("caption", ""))

    results = []
    results.append(post_to_instagram(image_url, caption))
    results.append(post_to_facebook(image_url, caption))
    results.append(post_to_youtube(image_url, concept))

    return results
