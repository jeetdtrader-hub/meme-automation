import os
import requests
import logging
import json
import re
import textwrap
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import random

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Meme color themes
THEMES = [
    {"bg": "#1a1a2e", "text": "#e94560", "sub": "#ffffff"},
    {"bg": "#0f3460", "text": "#e94560", "sub": "#ffffff"},
    {"bg": "#16213e", "text": "#f5a623", "sub": "#ffffff"},
    {"bg": "#2d132c", "text": "#ee4540", "sub": "#ffffff"},
    {"bg": "#1b262c", "text": "#0f4c75", "sub": "#ffffff"},
    {"bg": "#2c003e", "text": "#ff6b6b", "sub": "#ffffff"},
    {"bg": "#f7f7f7", "text": "#1a1a2e", "sub": "#e94560"},
    {"bg": "#fff3e0", "text": "#e65100", "sub": "#333333"},
]

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def generate_meme_image_local(concept: dict) -> str:
    """Generate meme image using Pillow — no external API needed!"""
    caption = concept.get("caption", "Meme Loading...")
    hashtags = concept.get("hashtags", "#meme #india")

    # Pick random theme
    theme = random.choice(THEMES)
    bg_color = hex_to_rgb(theme["bg"])
    text_color = hex_to_rgb(theme["text"])
    sub_color = hex_to_rgb(theme["sub"])

    # Canvas size — square for Instagram
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw gradient-like stripes for visual interest
    for i in range(0, H, 4):
        alpha = int(255 * (1 - i/H) * 0.15)
        stripe_color = tuple(min(255, c + 30) for c in bg_color)
        draw.rectangle([0, i, W, i+2], fill=stripe_color)

    # Draw top accent bar
    draw.rectangle([0, 0, W, 12], fill=text_color)
    draw.rectangle([0, H-12, W, H], fill=text_color)

    # Draw decorative corner elements
    for corner in [(20, 20), (W-20, 20), (20, H-20), (W-20, H-20)]:
        draw.ellipse([corner[0]-8, corner[1]-8, corner[0]+8, corner[1]+8], fill=text_color)

    # Watermark
    try:
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        font_main = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 62)
        font_hash = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except:
        font_small = ImageFont.load_default()
        font_main = ImageFont.load_default()
        font_hash = ImageFont.load_default()

    # MemeBot watermark top
    draw.text((W//2, 45), "🔥 MEMEBOT", font=font_small, fill=text_color, anchor="mm")

    # Main caption — wrap text
    max_chars = 28
    lines = textwrap.wrap(caption, width=max_chars)
    
    # Calculate total text height
    line_height = 80
    total_text_h = len(lines) * line_height
    start_y = (H - total_text_h) // 2 - 40

    # Draw shadow then text for each line
    for i, line in enumerate(lines):
        y = start_y + i * line_height
        # Shadow
        draw.text((W//2 + 3, y + 3), line, font=font_main, fill=(0,0,0), anchor="mm")
        # Main text
        draw.text((W//2, y), line, font=font_main, fill=sub_color, anchor="mm")

    # Divider line
    div_y = start_y + total_text_h + 30
    draw.rectangle([W//4, div_y, 3*W//4, div_y+3], fill=text_color)

    # Hashtags
    hash_text = hashtags[:60] + "..." if len(hashtags) > 60 else hashtags
    draw.text((W//2, div_y + 40), hash_text, font=font_hash, fill=text_color, anchor="mm")

    # Convert to base64 data URL
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    data_url = f"data:image/png;base64,{img_base64}"

    logger.info("✅ Meme image generated locally using Pillow!")
    return data_url


def generate_meme_concept(topic: str) -> dict:
    """Use Groq API (free) to generate a meme concept."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set")

    prompt = f"""You are a viral Indian meme creator. Create a funny meme for: {topic}

Reply with ONLY this JSON, nothing else, no explanation, no markdown:
{{"caption":"funny Hindi/Hinglish caption here","image_prompt":"cartoon scene description","hashtags":"#meme #india #funny #trending","platform_caption":"caption with hashtags"}}"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a JSON-only response bot. Never write anything except valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        },
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    text = data["choices"][0]["message"]["content"].strip()
    text = text.replace("```json", "").replace("```", "").strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        text = match.group(0)
    concept = json.loads(text)
    logger.info(f"✅ Meme concept generated for: {topic}")
    return concept


def generate_meme_image(concept: dict) -> str:
    """Generate meme image locally — always works, no external API!"""
    return generate_meme_image_local(concept)
