#!/usr/bin/env python3
"""
Crypto Degen Agent - Monitors SOL, altcoins, memecoins and sends alerts
"""
import os
import json
import urllib.request
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Coins to track - SOL + popular memecoins/altcoins
COINS = [
    "solana",
    "dogecoin",
    "shiba-inu",
    "pepe",
    "bonk",
    "dogwifcoin",
    "popcat",
    "jupiter",
    "raydium",
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        print("✅ Crypto alert sent")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

def get_prices():
    """Fetch prices from CoinGecko (free, no API key needed)."""
    ids = ",".join(COINS)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Price fetch error: {e}")
        return {}

def get_trending():
    """Get trending coins from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/search/trending"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            coins = data.get("coins", [])[:5]
            return [c["item"]["name"] + " (" + c["item"]["symbol"] + ")" for c in coins]
    except Exception as e:
        print(f"Trending fetch error: {e}")
        return []

def ai_degen_analysis(prices_text, trending):
    """Get AI degen take on the market."""
    if not GROQ_API_KEY:
        return ""

    prompt = f"""You are a crypto degen analyst giving a quick market update to Adedamola, a Nigerian crypto degen focused on Solana ecosystem and memecoins.

Current prices and 24h changes:
{prices_text}

Trending coins right now:
{', '.join(trending)}

Give him:
1. 🔥 Quick vibe check (1 sentence — is it a good degen day or not?)
2. 📊 SOL ecosystem summary (2 sentences)
3. 🚀 One memecoin/altcoin to watch today and why (be specific)
4. ⚠️ One risk to watch out for

Keep it short, punchy, degen-friendly. Use emojis. No financial advice disclaimer needed — he knows the risks."""

    data = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "max_tokens": 500,
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
        print(f"AI analysis error: {e}")
        return ""

def format_change(change):
    if change is None:
        return "N/A"
    arrow = "📈" if change > 0 else "📉"
    return f"{arrow} {change:+.2f}%"

def run():
    now = datetime.now().strftime("%H:%M UTC")
    print(f"🪙 Running crypto check at {now}...")

    prices = get_prices()
    trending = get_trending()

    if not prices:
        print("No price data available")
        return

    # Format prices
    coin_names = {
        "solana": "SOL",
        "dogecoin": "DOGE",
        "shiba-inu": "SHIB",
        "pepe": "PEPE",
        "bonk": "BONK",
        "dogwifcoin": "WIF",
        "popcat": "POPCAT",
        "jupiter": "JUP",
        "raydium": "RAY",
    }

    prices_text = ""
    price_lines = ""

    for coin_id, symbol in coin_names.items():
        if coin_id in prices:
            data = prices[coin_id]
            price = data.get("usd", 0)
            change = data.get("usd_24h_change", 0)
            change_str = format_change(change)

            # Flag big movers (>10% change)
            flag = " 🚨" if abs(change or 0) > 10 else ""
            price_lines += f"*{symbol}*: ${price:,.4f} {change_str}{flag}\n"
            prices_text += f"{symbol}: ${price} ({change:+.2f}% 24h)\n"

    # Get AI degen take
    ai_take = ai_degen_analysis(prices_text, trending)

    # Check for big movers to decide if urgent alert needed
    big_movers = [coin for coin, data in prices.items()
                  if abs(data.get("usd_24h_change") or 0) > 15]

    header = "🚨 *CRYPTO ALERT* 🚨" if big_movers else "🪙 *Crypto Degen Report*"

    trending_str = ", ".join(trending[:3]) if trending else "N/A"

    message = f"""{header} — {now}

{price_lines}
🔥 *Trending:* {trending_str}

{ai_take}"""

    send_telegram(message)
    print("✅ Crypto report sent!")

if __name__ == "__main__":
    run()
