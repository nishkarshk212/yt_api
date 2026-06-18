# YT-DLP Telegram Music Bot API

## Setup Instructions

### Local Development
1. **Install FFmpeg** (required for audio conversion):
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
   - Windows: Download from https://ffmpeg.org/

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create .env file**:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   ```

4. **Start the API server**:
   ```bash
   python api.py
   ```

## Deploying to Vercel
1. **Push your code to GitHub**
2. **Connect your repository to Vercel**
3. **Add environment variables in Vercel**:
   - `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
4. **Deploy!**

## Setting Up Telegram Webhook
After deploying to Vercel, set the webhook URL for your Telegram bot using this request (replace with your actual Vercel URL):
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://yt-api-two-plum.vercel.app/telegram/webhook
```

## API Endpoints
- `GET /` - Root endpoint
- `GET /check` - Check if API is running
- `GET /info?url=<VIDEO_URL>` - Get audio information
- `GET /download?url=<VIDEO_URL>` - Download audio as MP3
- `POST /telegram/webhook` - Telegram bot webhook

## Bot Commands
- `/start` - Welcome message
- `/check` - Check if bot is alive

## How to Use
- Send a YouTube (or other yt-dlp supported) link to the bot
- The bot will download and send you the MP3 audio
