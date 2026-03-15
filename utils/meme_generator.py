import os
import requests
import logging
import json
import urllib.parse
import re

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


def generate_meme_concept(topic: str) -> dict:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set")

    prompt = f"Create a funny Indian meme about: {topic}. Reply with only valid JSON like this example: {{\"caption\": \"When petrol price goes up again\", \"image_prompt\": \"shocked Indian man at petrol pump cartoon\", \"hashtags\": \"#meme #india #funny\", \"platform_caption\": \"When petrol price goes up again #meme #india #funny\"}}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.5,
                "maxOutputTokens": 200,
                "responseMimeType": "application/json"
            }
        },
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    concept = json.loads(text)
    return concept


def generate_meme_image(concept: dict) -> str:
    image_prompt = concept.get("image_prompt", "funny Indian cartoon meme")
    full_prompt = f"{image_prompt}, funny Indian cartoon style, vibrant colors"
    encoded_prompt = urllib.parse.quote(full_prompt)
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true"
