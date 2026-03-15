#!/usr/bin/env python3
"""
Writing Assistant Bot - Always-on webhook version for Railway/Koyeb
Falls back to polling for GitHub Actions
"""
import os
import json
import urllib.request
import urllib.error
import time
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

SYSTEM_PROMPT = """You are MoltyMagma, Adedamola's personal AI assistant. He is a Nigerian writer, crypto degen, vibecoder, and AI consultant-in-training based in Abuja.

Your personality: Sharp, witty, practical, encouraging, Nigeria-aware. You have a cool degen energy. You remember you're called MoltyMagma.

Your capabilities:
- Writing: blog posts, tweets/X threads, LinkedIn posts, newsletters, scripts, cold emails, copy
- Crypto: Solana ecosystem, memecoins, DeFi, market takes, degen strategies
- Vibe coding: no-code tools, AI tool recommendations, prompting strategies
- AI consulting: pitches, proposals, client strategies for Nigerian/African market
- General assistant: research, planning, brainstorming, advice

Rules:
- Always be concise for Telegram
- Use emojis naturally
- If asked to write something, just write it — don't ask too many questions
- Be direct and useful, not corporate
- You know Adedamola personally — you're his guy"""

def send_telegram(chat_id, message, reply_to=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    if len(message) > 4000:
        message = message[:4000] + "...\n\n_[Ask me to continue]_"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f"Send error: {e}")
        return False

def get_ai_response(user_message, retries=3):
    """Get AI response with retry logic."""
    for attempt in range(retries):
        try:
            data = json.dumps({
                "model": "llama-3.1-8b-instant",
                "max_tokens": 1000,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ]
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                }
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                return result["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code == 403:
                # Rate limited - wait and retry
                wait = (attempt + 1) * 5
                print(f"Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            return f"I'm having a moment — try again in a bit! 🙏"
        except Exception as e:
            print(f"AI error attempt {attempt+1}: {e}")
            if attempt < retries - 1:
                time.sleep(3)
    return "I hit my limit for now — ask me again in a minute! ⏳"

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?timeout=5&limit=10"
    if offset:
        url += f"&offset={offset}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"getUpdates error: {e}")
        return {"ok": False, "result": []}

def load_offset():
    try:
        with open("/tmp/last_offset.txt") as f:
            return int(f.read().strip())
    except:
        return None

def save_offset(offset):
    with open("/tmp/last_offset.txt", "w") as f:
        f.write(str(offset))

def handle_message(text, chat_id, message_id):
    """Handle incoming message and send response."""
    text = text.strip()

    if text.startswith("/start"):
        response = """👋 *Yo, I'm MoltyMagma — your personal AI agent!*

Here's what I do for you:

✍️ *Write* — threads, posts, emails, copy
🪙 *Degen* — SOL, memecoins, market takes  
👨‍💻 *Vibe code* — AI tools, no-code, prompts
🤖 *AI consulting* — pitches, proposals, strategy

Plus automatic updates daily:
• 🌅 7AM — Job opportunities
• 📊 9AM & 6PM — Crypto report
• 📰 8AM — AI news digest

Just talk to me normally. What do you need? 🚀"""

    elif text.startswith("/status"):
        response = f"✅ *MoltyMagma Online* — {datetime.now().strftime('%H:%M UTC, %b %d')}\n\nAll systems running. What do you need? 🔥"

    elif text.startswith("/help"):
        response = """*Commands:*
/start — Introduction
/status — Check if I'm alive
/help — This message

Or just talk to me naturally:
• "Write a tweet about..."
• "What's happening with SOL?"
• "Help me pitch AI consulting to..."
• "Draft a cold email for..."

I got you 💪"""

    else:
        # Show typing indicator
        typing_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
        typing_data = json.dumps({"chat_id": chat_id, "action": "typing"}).encode()
        try:
            urllib.request.urlopen(
                urllib.request.Request(typing_url, data=typing_data,
                headers={"Content-Type": "application/json"}), timeout=5)
        except:
            pass
        response = get_ai_response(text)

    send_telegram(chat_id, response, reply_to=message_id)

def run():
    """Polling mode for GitHub Actions."""
    print("🤖 MoltyMagma checking messages...")
    offset = load_offset()
    updates = get_updates(offset)

    if not updates.get("ok"):
        print("Failed to get updates")
        return

    results = updates.get("result", [])
    if not results:
        print("No new messages")
        return

    print(f"Found {len(results)} update(s)")

    for update in results:
        update_id = update.get("update_id")
        message = update.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")
        message_id = message.get("message_id")
        from_user = message.get("from", {}).get("first_name", "User")

        if not text or not chat_id:
            save_offset(update_id + 1)
            continue

        if str(chat_id) != str(TELEGRAM_CHAT_ID):
            save_offset(update_id + 1)
            continue

        print(f"Processing: '{text[:50]}' from {from_user}")
        handle_message(text, chat_id, message_id)
        save_offset(update_id + 1)
        # Small delay between messages to avoid rate limits
        time.sleep(2)

    print("✅ Done!")

if __name__ == "__main__":
    run()
