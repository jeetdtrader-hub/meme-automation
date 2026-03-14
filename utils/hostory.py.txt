import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'history.json')

def load_history() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_to_history(topic: str, concept: dict, image_url: str, result: list):
    history = load_history()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "caption": concept.get("caption", ""),
        "image_url": image_url,
        "hashtags": concept.get("hashtags", ""),
        "post_results": result
    }
    history.insert(0, entry)
    history = history[:50]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)