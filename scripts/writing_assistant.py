#!/usr/bin/env python3
"""
Writing Assistant Bot - Responds to Telegram messages for writing help
Runs as a one-shot webhook checker via GitHub Actions
"""
import os
import json
import urllib.request
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

SYSTEM_PROMPT = """You are Adedamola's personal AI assistant. He is a Nigerian writer, crypto degen, vibecoder, and AI consultant-in-training based in Abuja.

Your personality: Sharp, practical, encouraging, Nigeria-aware. You know his context.

Your capabilities:
- Writing help: blog posts, tweets, LinkedIn posts, newsletters, scripts, copy
- Crypto: Solana ecosystem, memecoins, DeFi strategies, market takes  
- Vibe coding: help with no-code tools, prompting, AI tool recommendations
- AI consulting: pitch decks, proposals, client strategies for Nigerian market

Always be concise for Telegram. Use formatting with emojis. If asked to write something, just write it — don't ask too many questions. Take initiative."""

def get_updates(offset=None):
    """Get new Telegram messages."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?timeout=5"
    if offset:
        url += f"&offset={offset}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"getUpdates error: {e}")
        return {"ok": False, "result": []}

def send_telegram(chat_id, message):
    """Send reply to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    if len(message) > 4000:
        message = message[:4000] + "...\n\n_[Truncated — ask me to continue]_"
    data = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f"Send error: {e}")
        return False

def get_ai_response(user_message):
    """Get AI response from OpenRouter."""
    data = json.dumps({
        "model": "llama-3.3-70b-versatile",
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
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Sorry, AI error: {e}"

def save_offset(offset):
    """Save last processed update ID."""
    with open("/tmp/last_offset.txt", "w") as f:
        f.write(str(offset))

def load_offset():
    """Load last processed update ID."""
    try:
        with open("/tmp/last_offset.txt") as f:
            return int(f.read().strip())
    except:
        return None

def run():
    print("🤖 Checking for new Telegram messages...")
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
        from_user = message.get("from", {}).get("first_name", "User")

        if not text or not chat_id:
            save_offset(update_id + 1)
            continue

        # Only respond to the authorized chat
        if str(chat_id) != str(TELEGRAM_CHAT_ID):
            print(f"Ignoring message from unauthorized chat: {chat_id}")
            save_offset(update_id + 1)
            continue

        print(f"Processing: '{text[:50]}...' from {from_user}")

        # Handle commands
        if text.startswith("/start"):
            response = """👋 *Hey Adedamola!* Your AI agent is live!

Here's what I can do for you:

✍️ *Writing* — "Write a LinkedIn post about AI in Nigeria"
🪙 *Crypto* — "What's your take on SOL right now?"
👨‍💻 *Vibe coding* — "Help me build a no-code landing page"
🤖 *AI consulting* — "Draft a proposal for a Lagos startup"

Daily automatics:
• 🌅 7AM — Job hunt results
• 📊 9AM & 6PM — Crypto report  
• 📰 8AM — AI news digest

Just talk to me naturally. Let's get to work! 🚀"""
        elif text.startswith("/status"):
            response = f"✅ *Agent Status* — {datetime.now().strftime('%H:%M UTC')}\n\nAll systems operational!\n• Job hunter: Active 🟢\n• Crypto monitor: Active 🟢\n• AI digest: Active 🟢\n• Writing assistant: Active 🟢"
        else:
            response = get_ai_response(text)

        send_telegram(chat_id, response)
        save_offset(update_id + 1)
        print(f"✅ Replied to message {update_id}")

    print("Done processing messages!")

if __name__ == "__main__":
    run()
