# YT-DLP Telegram Music Bot API

## Two Ways to Use the Bot

### Option 1: Use the Webhook (Deployed on Vercel)
This is the easier option if you already have the API deployed on Vercel!

### Option 2: Run a Standalone Bot (locally or on a server)
This uses `bot.py` which connects to the API (local or Vercel)

---

## Step 1: Get a Telegram Bot Token
1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the instructions
3. BotFather will give you a **bot token** - save this!

---

## Option 1: Setup Webhook (Vercel Deployment)
1. Make sure your API is deployed on Vercel (you already did this!)
2. Set the webhook URL by visiting this link in your browser (replace placeholders):
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<YOUR_VERCEL_URL>/telegram/webhook
   ```
   Example:
   ```
   https://api.telegram.org/bot123456789:ABCdefGhIJKlmNoPQRStuvWxyz123456/setWebhook?url=https://yt-api-two-plum.vercel.app/telegram/webhook
   ```
3. That's it! Now send a YouTube link to your bot on Telegram!

---

## Option 2: Run Standalone Bot
1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Create .env file** (copy from .env.example):
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   API_BASE_URL=https://yt-api-two-plum.vercel.app  # or your local http://localhost:8000
   ```
3. **Start the bot**:
   ```bash
   python bot.py
   ```

---

## API Endpoints
- `GET /` - Root endpoint
- `GET /check` - Check if API is running
- `GET /info?url=<VIDEO_URL>` - Get audio information
- `GET /download?url=<VIDEO_URL>` - Download audio
- `POST /telegram/webhook` - Telegram bot webhook

## Bot Commands
- `/start` - Welcome message
- `/check` or `/ping` - Check if bot is alive

## How to Use
- Send a YouTube (or other yt-dlp supported) link to the bot
- The bot will download and send you the audio!
