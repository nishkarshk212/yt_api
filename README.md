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
   API_BASE_URL=http://localhost:8000
   ```

4. **Start the API server**:
   ```bash
   python api.py
   ```

5. **Start the Telegram bot** (in a new terminal):
   ```bash
   python bot.py
   ```

## Deploying to Vercel
1. **Push your code to GitHub**
2. **Connect your repository to Vercel**
3. **Add environment variables in Vercel**:
   - `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
4. **Deploy!**

## Bot Commands
- `/start` - Welcome message
- `/ping` - Check if bot is alive

## How to Use
- Send a YouTube (or other yt-dlp supported) link to the bot
- The bot will download and send you the MP3 audio
