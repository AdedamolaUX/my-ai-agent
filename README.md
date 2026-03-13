# 🤖 Adedamola's Personal AI Agent

Your autonomous AI assistant that works 24/7 without you having to prompt it.

## What It Does

| Agent | Schedule | Task |
|-------|----------|------|
| 🔍 Job Hunter | Daily 7AM WAT | Searches remote writing, AI, Web3, vibe coding jobs |
| 🪙 Crypto Monitor | 9AM & 6PM WAT | SOL + memecoin prices, trends, degen analysis |
| 📰 AI Digest | Daily 8AM WAT | AI industry news with consulting angles |
| ✍️ Writing Assistant | Every 15 mins | Responds to your Telegram messages |

## Setup (One Time Only)

### Step 1 — Get Your Keys

**OpenRouter API Key (Free AI)**
1. Go to console.groq.com → Sign up
2. Click Keys → Create Key → copy it

**Telegram Bot Token**
1. Open Telegram → search @BotFather
2. Type /newbot → follow prompts
3. Copy the token it gives you

**Your Telegram Chat ID**
1. Open Telegram → search @userinfobot
2. Start it → it sends you your Chat ID
3. Copy that number

### Step 2 — Create GitHub Repository

1. Go to github.com → Click "New repository"
2. Name it: `my-ai-agent`
3. Make it **Private**
4. Click "Create repository"

### Step 3 — Upload These Files

1. Click "uploading an existing file" on your new repo page
2. Drag and drop ALL the files from this folder
3. Click "Commit changes"

### Step 4 — Add Your Secret Keys

In your GitHub repo:
1. Click **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"** and add these 3 secrets:

| Secret Name | Value |
|-------------|-------|
| `TELEGRAM_TOKEN` | Your BotFather token |
| `TELEGRAM_CHAT_ID` | Your chat ID number |
| `GROQ_API_KEY` | Your gsk_... key |

### Step 5 — Enable GitHub Actions

1. Click the **Actions** tab in your repo
2. Click **"I understand my workflows, go ahead and enable them"**

### Step 6 — Test It!

1. Click **Actions** → **"Adedamola's AI Agent"**
2. Click **"Run workflow"** → **"Run workflow"**
3. Check your Telegram — you should get a message within 2 minutes!

Then open your bot on Telegram and type `/start`

## Talking to Your Assistant

Just message your Telegram bot naturally:

- "Write a Twitter thread about AI tools for Nigerian freelancers"
- "What's the vibe on SOL today?"  
- "Help me write a cold email to pitch AI consulting to a Lagos fintech"
- "Summarize what happened in AI this week"
- `/status` — check if agent is running

## Costs

- GitHub Actions: **FREE** (2,000 mins/month)
- OpenRouter free models: **FREE**
- CoinGecko API: **FREE**
- Telegram: **FREE**
- Total: **$0/month** 🎉
