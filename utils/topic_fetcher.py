import os
import requests
import feedparser
import logging

logger = logging.getLogger(__name__)

NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")

def fetch_trending_topics():
    """Fetch trending topics from NewsAPI (India focused) or Google Trends RSS fallback."""
    topics = []

    # Try NewsAPI first
    if NEWS_API_KEY:
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "country": "in",
                "pageSize": 10,
                "apiKey": NEWS_API_KEY
            }
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                topics = [a["title"] for a in articles if a.get("title")]
                logger.info(f"✅ Fetched {len(topics)} topics from NewsAPI")
                return topics[:10]
        except Exception as e:
            logger.warning(f"NewsAPI failed: {e}, falling back to RSS")

    # Fallback: Google Trends RSS (India)
    try:
        feed = feedparser.parse("https://trends.google.com/trending/rss?geo=IN")
        topics = [entry.title for entry in feed.entries]
        logger.info(f"✅ Fetched {len(topics)} topics from Google Trends RSS")
        return topics[:10]
    except Exception as e:
        logger.error(f"Google Trends RSS failed: {e}")

    # Final fallback: hardcoded Indian trending topics
    return [
        "IPL 2025 latest match",
        "Indian Budget 2025",
        "Petrol price hike India",
        "Bollywood latest news",
        "Cricket World Cup India"
    ]
