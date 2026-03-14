import os
import json
import logging
from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from utils.topic_fetcher import fetch_trending_topics
from utils.meme_generator import generate_meme_concept, generate_meme_image
from utils.poster import post_to_all_platforms
from utils.history import load_history, save_to_history
import atexit

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scheduler for auto-posting
scheduler = BackgroundScheduler()

def automated_meme_job():
    """Fully automated meme generation and posting job."""
    logger.info("🤖 Running automated meme job...")
    try:
        topics = fetch_trending_topics()
        if not topics:
            logger.warning("No trending topics found.")
            return

        topic = topics[0]
        concept = generate_meme_concept(topic)
        image_url = generate_meme_image(concept)
        result = post_to_all_platforms(image_url, concept)
        save_to_history(topic, concept, image_url, result)
        logger.info(f"✅ Meme posted for topic: {topic}")
    except Exception as e:
        logger.error(f"❌ Automated job failed: {e}")

# Schedule: 3 times a day (8am, 1pm, 7pm)
scheduler.add_job(automated_meme_job, 'cron', hour='8,13,19', minute=0)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


@app.route('/')
def index():
    history = load_history()
    return render_template('index.html', history=history)


@app.route('/api/trending', methods=['GET'])
def get_trending():
    topics = fetch_trending_topics()
    return jsonify({"topics": topics})


@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    topic = data.get('topic', '').strip()
    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    try:
        concept = generate_meme_concept(topic)
        image_url = generate_meme_image(concept)
        return jsonify({"concept": concept, "image_url": image_url})
    except Exception as e:
        logger.error(f"Generate error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/post', methods=['POST'])
def post_meme():
    data = request.json
    image_url = data.get('image_url')
    concept = data.get('concept')
    topic = data.get('topic', 'trending')

    if not image_url or not concept:
        return jsonify({"error": "image_url and concept are required"}), 400

    try:
        result = post_to_all_platforms(image_url, concept)
        save_to_history(topic, concept, image_url, result)
        return jsonify({"result": result})
    except Exception as e:
        logger.error(f"Post error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/automate', methods=['POST'])
def trigger_auto():
    """Manually trigger the automated job."""
    try:
        automated_meme_job()
        return jsonify({"status": "success", "message": "Automated meme job triggered!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(load_history())


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
