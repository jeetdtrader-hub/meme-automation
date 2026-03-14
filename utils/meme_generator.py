import os
import requests
import logging
import json
import urllib.parse

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


def generate_meme_concept(topic: str) -> dict:
    """Use Claude API to generate a meme concept for the given topic."""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set")

    prompt = f"""You are a viral Indian meme creator. Given a trending topic, create a funny, relatable meme concept.

Topic: {topic}

Respond ONLY with a JSON object, no markdown, no explanation:
{{
  "caption": "The funny meme caption (Hindi/Hinglish/English, max 2 lines)",
  "image_prompt": "Detailed prompt for AI image generation - cartoon/illustration style, funny Indian character, describe the scene clearly, keep under 200 characters",
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
    """Generate cartoon meme image using Pollinations.ai (FREE, no API key needed)."""
    
    image_prompt = concept.get("image_prompt", "funny Indian cartoon meme")
    caption = concept.get("caption", "")

    # Build enhanced prompt for cartoon meme style
    full_prompt = (
        f"{image_prompt}, "
        f"funny Indian cartoon illustration style, "
        f"vibrant colors, expressive characters, meme format, "
        f"bold clean composition, high quality digital art"
    )

    # URL encode the prompt
    encoded_prompt = urllib.parse.quote(full_prompt)
    
    # Pollinations.ai free image generation URL
    # width=1024, height=1024 for square meme format
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true&enhance=true"
    
    logger.info(f"✅ Meme image URL generated via Pollinations.ai")
    return image_url
