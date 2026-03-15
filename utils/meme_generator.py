import os
import requests
import logging
import json
import urllib.parse
import re

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


def clean_text(text):
    """Remove special characters that break JSON."""
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2013', '-').replace('\u2014', '-')
    text = text.replace('\n', ' ').replace('\r', ' ')
    # Remove any control characters
    text = re.sub(r'[\x00-\x1f\x7f]', ' ', text)
    return text


def generate_meme_concept(topic: str) -> dict:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set")

    prompt = f"""Create a funny Indian meme for topic: {topic}

Reply with ONLY this JSON, nothing else:
{{"caption":"funny caption here","image_prompt":"cartoon scene description here","hashtags":"#meme #india #funny","platform_caption":"caption with hashtags"}}"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 300
            }
        },
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    text = text.replace("```json", "").replace("```", "").strip()
    text = clean_text(text)
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        text = match.group(0)
    concept = json.loads(text)
    logger.info(f"Meme concept generated for: {topic}")
    return concept


def generate_meme_image(concept: dict) -> str:
    image_prompt = concept.get("image_prompt", "funny Indian cartoon meme")
    full_prompt = (
        f"{image_prompt}, funny Indian cartoon style, "
        f"vibrant colors, expressive characters, high quality"
    )
    encoded_prompt = urllib.parse.quote(full_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true"
    logger.info(f"Meme image URL generated")
    return image_url
