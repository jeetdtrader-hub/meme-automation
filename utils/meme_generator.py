import os
import requests
import logging
import json
import urllib.parse
import re

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


def generate_meme_concept(topic: str) -> dict:
    """Use Gemini API to generate a meme concept for the given topic."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set")

    prompt = f"""You are a viral Indian meme creator. Given a trending topic, create a funny, relatable meme concept.

Topic: {topic}

You MUST respond with ONLY a valid JSON object. No markdown, no backticks, no explanation before or after.
Use only simple ASCII characters in the JSON. No special quotes or unicode punctuation.

{{
  "caption": "funny meme caption here max 2 lines",
  "image_prompt": "cartoon image description here under 150 characters",
  "hashtags": "#meme #india #trending #funny",
  "platform_caption": "full caption with hashtags here"
}}"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 400
            }
        },
        timeout=30
    )
    response.raise_for_status()
    data = response.json()

    # Extract text from Gemini response
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Clean markdown backticks
    text = text.replace("```json", "").replace("```", "").strip()

    # Extract JSON object using regex if extra text present
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        text = match.group(0)

    # Replace smart quotes with regular quotes
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')

    concept = json.loads(text)
    logger.info(f"✅ Meme concept generated for: {topic}")
    return concept


def generate_meme_image(concept: dict) -> str:
    """Generate cartoon meme image using Pollinations.ai (FREE, no API key needed)."""

    image_prompt = concept.get("image_prompt", "funny Indian cartoon meme")

    full_prompt = (
        f"{image_prompt}, "
        f"funny Indian cartoon illustration style, "
        f"vibrant colors, expressive characters, meme format, "
        f"bold clean composition, high quality digital art"
    )

    encoded_prompt = urllib.parse.quote(full_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true&enhance=true"

    logger.info(f"✅ Meme image URL generated via Pollinations.ai")
    return image_url
