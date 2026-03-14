import os
import requests
import logging
import json

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
IDEOGRAM_API_KEY = os.environ.get("IDEOGRAM_API_KEY", "")


def generate_meme_concept(topic: str) -> dict:
    """Use Claude API to generate a meme concept for the given topic."""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set")

    prompt = f"""You are a viral Indian meme creator. Given a trending topic, create a funny, relatable meme concept.

Topic: {topic}

Respond ONLY with a JSON object, no markdown, no explanation:
{{
  "caption": "The funny meme caption (Hindi/Hinglish/English, max 2 lines)",
  "image_prompt": "Detailed prompt for AI image generation - cartoon/illustration style, funny Indian character, describe the scene clearly",
  "hashtags": "#meme #india #trending (relevant hashtags, 10-15)",
  "platform_caption": "Full Instagram/Facebook caption with caption + hashtags"
}}"""

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    text = data["content"][0]["text"].strip()

    # Clean any accidental markdown
    text = text.replace("```json", "").replace("```", "").strip()
    concept = json.loads(text)
    logger.info(f"✅ Meme concept generated for: {topic}")
    return concept


def generate_meme_image(concept: dict) -> str:
    """Generate cartoon meme image using Ideogram API."""
    if not IDEOGRAM_API_KEY:
        logger.warning("IDEOGRAM_API_KEY not set, returning placeholder")
        return "https://placehold.co/1080x1080/FF6B35/white?text=Meme+Coming+Soon"

    image_prompt = concept.get("image_prompt", "")
    caption = concept.get("caption", "")

    # Enhance prompt for better meme style
    full_prompt = (
        f"{image_prompt}. "
        f"Caption text on image: '{caption}'. "
        f"Style: Indian cartoon illustration, funny and expressive characters, "
        f"bold text overlay, vibrant colors, meme format, high quality, 1:1 ratio"
    )

    try:
        response = requests.post(
            "https://api.ideogram.ai/generate",
            headers={
                "Api-Key": IDEOGRAM_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "image_request": {
                    "prompt": full_prompt,
                    "aspect_ratio": "ASPECT_1_1",
                    "model": "V_2",
                    "style_type": "ILLUSTRATION",
                    "magic_prompt_option": "ON"
                }
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        image_url = data["data"][0]["url"]
        logger.info(f"✅ Meme image generated: {image_url}")
        return image_url
    except Exception as e:
        logger.error(f"Ideogram API error: {e}")
        return "https://placehold.co/1080x1080/FF6B35/white?text=Meme+Coming+Soon"
