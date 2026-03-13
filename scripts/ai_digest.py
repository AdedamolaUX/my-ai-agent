#!/usr/bin/env python3
"""
AI News Digest Agent - Daily AI industry news for Adedamola's consulting work
"""
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # Split long messages
    if len(message) > 4000:
        message = message[:4000] + "...\n\n_[Message truncated]_"
    data = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        print("✅ AI digest sent")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

def fetch_hackernews_ai():
    """Get top AI stories from Hacker News (free API)."""
    try:
        # Get top stories
        req = urllib.request.Request(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            story_ids = json.loads(resp.read().decode())[:50]

        ai_stories = []
        ai_keywords = ["ai", "llm", "gpt", "claude", "gemini", "openai", "anthropic",
                       "agent", "ml", "machine learning", "neural", "model", "chatbot",
                       "web3", "crypto", "blockchain", "solana", "defi"]

        for sid in story_ids[:30]:
            try:
                req = urllib.request.Request(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    story = json.loads(resp.read().decode())
                    title = (story.get("title") or "").lower()
                    if any(kw in title for kw in ai_keywords):
                        ai_stories.append({
                            "title": story.get("title"),
                            "url": story.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                            "score": story.get("score", 0)
                        })
                        if len(ai_stories) >= 8:
                            break
            except:
                continue

        return sorted(ai_stories, key=lambda x: x["score"], reverse=True)[:6]
    except Exception as e:
        print(f"HN fetch error: {e}")
        return []

def ai_consulting_digest(stories_text):
    """Use AI to create a consultant-grade digest."""
    if not GROQ_API_KEY:
        return stories_text

    prompt = f"""You are an AI industry analyst helping Adedamola, a Nigerian AI enthusiast building his AI consulting career.

Here are today's top AI and tech stories:
{stories_text}

Create a quick consulting-grade briefing for him with:

1. 📌 *Today's Biggest Story* — What's the most important development and why it matters for businesses (2 sentences)
2. 💼 *Consulting Opportunity* — One concrete way he could pitch AI services to Nigerian businesses based on today's news (2 sentences)  
3. 🧠 *What to Know* — 2-3 bullet points of key facts he should know to sound sharp in conversations today
4. 🔗 *Must Read* — The single most important link from the list

Keep it practical, actionable, and Nigeria-context-aware where possible. He's early-career, building credibility."""

    data = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "max_tokens": 700,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}",
            
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI digest error: {e}")
        return stories_text

def run():
    today = datetime.now().strftime("%A, %B %d %Y")
    print(f"📰 Fetching AI news for {today}...")

    stories = fetch_hackernews_ai()

    if not stories:
        send_telegram(f"📰 *AI Digest — {today}*\n\nNo major AI stories found today. Good day to create content! ✍️")
        return

    stories_text = "\n".join([f"- {s['title']} (score: {s['score']}) | {s['url']}" for s in stories])

    digest = ai_consulting_digest(stories_text)

    message = f"""🤖 *AI & Tech Digest — {today}*

{digest}

_Stay sharp, stay ahead. You're becoming the AI consultant Nigeria needs._ 🇳🇬"""

    send_telegram(message)
    print("✅ AI digest complete!")

if __name__ == "__main__":
    run()
