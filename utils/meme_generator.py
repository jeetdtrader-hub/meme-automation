import os
import requests
import logging
import json
import urllib.parse
import re

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


def generate_meme_concept(topic: str) -> dict:
    """Use Groq API (free) to generate a meme concept."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set")

    prompt = f"""You are a viral Indian meme creator. Create a funny meme for: {topic}

Reply with ONLY this JSON, nothing else, no explanation, no markdown:
{{"caption":"funny Hindi/Hinglish caption here","image_prompt":"cartoon scene description under 150 chars","hashtags":"#meme #india #funny #trending","platform_caption":"caption with hashtags"}}"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a JSON-only response bot. You never write anything except valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 300
        },
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    text = data["choices"][0]["message"]["content"].strip()

    # Clean any accidental markdown
    text = text.replace("```json", "").replace("```", "").strip()

    # Extract JSON using regex
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        text = match.group(0)

    concept = json.loads(text)
    logger.info(f"✅ Meme concept generated for: {topic}")
    return concept


def generate_meme_image(concept: dict) -> str:
    """Generate cartoon meme image using Pollinations.ai (FREE)."""
    image_prompt = concept.get("image_prompt", "funny Indian cartoon meme")

    full_prompt = (
        f"{image_prompt}, "
        f"funny Indian cartoon illustration style, "
        f"vibrant colors, expressive characters, meme format, "
        f"bold clean composition, high quality digital art"
    )

    encoded_prompt = urllib.parse.quote(full_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true"

    logger.info(f"✅ Meme image URL generated via Pollinations.ai")
    return image_url
