# 🔥 MemeBot — Auto Meme Machine

Fully automated meme generation and posting pipeline.
**Topic → Claude AI → Cartoon Image → Instagram + Facebook + YouTube**

---

## 🚀 Quick Setup

### 1. Clone & Install
```bash
git clone <your-repo>
cd meme-autobot
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 3. Run Locally
```bash
python app.py
# Visit http://localhost:5000
```

---

## 🔑 API Keys Needed

| Key | Where to Get | Cost |
|-----|-------------|------|
| `ANTHROPIC_API_KEY` | console.anthropic.com | Pay per use |
| `IDEOGRAM_API_KEY` | ideogram.ai | Free tier available |
| `NEWS_API_KEY` | newsapi.org | Free tier (100 req/day) |
| `META_ACCESS_TOKEN` | developers.facebook.com | Free |
| `INSTAGRAM_ACCOUNT_ID` | Meta Business Suite | Free |
| `FACEBOOK_PAGE_ID` | Facebook Page Settings | Free |

---

## 📱 Meta Setup (Instagram + Facebook)

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create an App → Business type
3. Add **Instagram Graph API** and **Pages API** products
4. Generate a **Long-Lived Page Access Token** (valid 60 days)
5. Get your **Instagram Business Account ID** from the Graph API Explorer
6. Get your **Facebook Page ID** from Page Settings → About

> ⚠️ Your Instagram must be a **Professional/Business account** linked to a Facebook Page

---

## 🤖 How Automation Works

The scheduler runs 3 times per day (8AM, 1PM, 7PM):
1. Fetches top trending Indian news via NewsAPI
2. Sends topic to Claude → generates funny caption + image prompt
3. Sends image prompt to Ideogram → generates cartoon meme
4. Posts to Instagram + Facebook automatically

You can also **manually trigger** any step from the dashboard.

---

## 🚢 Deploy to Render

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Add all environment variables in Render dashboard
5. Deploy!

The `render.yaml` file handles the rest.

---

## 📁 Project Structure

```
meme-autobot/
├── app.py                 # Flask app + scheduler
├── requirements.txt
├── render.yaml            # Render deployment config
├── .env.example           # Environment variables template
├── templates/
│   └── index.html         # Dashboard UI
└── utils/
    ├── topic_fetcher.py   # NewsAPI + Google Trends RSS
    ├── meme_generator.py  # Claude API + Ideogram
    ├── poster.py          # Meta Graph API posting
    └── history.py         # Local history storage
```
