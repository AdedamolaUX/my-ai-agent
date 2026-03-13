#!/usr/bin/env python3
"""
Job Hunter Agent - Searches for remote jobs and sends to Telegram
"""
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

JOB_SEARCHES = [
    {"query": "remote content writer", "label": "✍️ Writing/Content"},
    {"query": "remote AI consultant", "label": "🤖 AI Consultant"},
    {"query": "remote web3 crypto", "label": "🪙 Web3/Crypto"},
    {"query": "remote vibe coder no-code AI tools", "label": "👨‍💻 Vibe Coding"},
]

def send_telegram(message):
    """Send message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        print("✅ Telegram message sent")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

def search_remotive_jobs(query):
    """Search Remotive.com for remote jobs (free API)."""
    encoded = urllib.parse.quote(query)
    url = f"https://remotive.com/api/remote-jobs?search={encoded}&limit=3"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get("jobs", [])
    except Exception as e:
        print(f"Search error for '{query}': {e}")
        return []

def search_crypto_jobs(query):
    """Search crypto-specific jobs from Web3.career (free)."""
    encoded = urllib.parse.quote(query)
    url = f"https://remotive.com/api/remote-jobs?search={encoded}&category=software-dev&limit=3"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get("jobs", [])
    except Exception as e:
        print(f"Crypto job search error: {e}")
        return []

def ai_filter_jobs(jobs_text):
    """Use OpenRouter AI to filter and summarize the best jobs."""
    if not GROQ_API_KEY:
        return jobs_text

    prompt = f"""You are Adedamola's personal job hunting assistant. He is a Nigerian writer, AI enthusiast, crypto degen, and vibecoder building toward AI consulting.

Here are today's remote job listings. Pick the TOP 5 most relevant for him, prioritizing:
- High pay potential
- Remote/async work
- Matches his skills: writing, AI, crypto/Web3, no-code tools
- Entry to mid-level AI consulting roles

For each job give:
- Job title and company
- Why it's a good fit for him (1 sentence)
- The application link

Jobs:
{jobs_text}

Be concise and encouraging. End with a motivational one-liner."""

    data = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "max_tokens": 1000,
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
        print(f"AI filter error: {e}")
        return jobs_text

def run():
    today = datetime.now().strftime("%A, %B %d %Y")
    print(f"🔍 Starting job hunt for {today}...")

    all_jobs_text = ""
    total_found = 0

    for search in JOB_SEARCHES:
        jobs = search_remotive_jobs(search["query"])
        if jobs:
            all_jobs_text += f"\n\n=== {search['label']} ===\n"
            for job in jobs:
                title = job.get("title", "N/A")
                company = job.get("company_name", "N/A")
                link = job.get("url", "#")
                salary = job.get("salary", "Not specified")
                all_jobs_text += f"- {title} at {company} | Salary: {salary} | {link}\n"
                total_found += 1

    if total_found == 0:
        send_telegram("🔍 *Job Hunt Update*\n\nNo new jobs found today. I'll check again tomorrow! Keep building 💪")
        return

    # Use AI to filter and personalize
    filtered = ai_filter_jobs(all_jobs_text)

    message = f"""🎯 *Daily Job Hunt — {today}*
Found {total_found} opportunities across your target roles!

{filtered}

_Apply to at least 2 today. Consistency beats perfection! 🚀_"""

    send_telegram(message)
    print("✅ Job hunt complete!")

if __name__ == "__main__":
    run()
