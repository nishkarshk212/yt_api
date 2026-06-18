import os
import httpx
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🎵 Hi {user.first_name}! 👋\n\n"
        "✅ I'm your YouTube Music Downloader Bot!\n\n"
        "📥 Just send me any YouTube (or other supported site) link and I'll send you the audio in MP3 format!\n\n"
        "Commands:\n"
        "• /start - Show this welcome message\n"
        "• /ping - Check if I'm alive"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏓 Pong!\n\n✅ Bot is running perfectly!\nAPI Status: Connected"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Please send a valid URL starting with http:// or https://")
        return

    status_message = await update.message.reply_text("🔍 Fetching audio info...")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            info_response = await client.get(f"{API_BASE_URL}/info", params={"url": url})
            info = info_response.json()
            
            await status_message.edit_text(f"⏳ Downloading: {info['title']}...")
            
            download_response = await client.get(f"{API_BASE_URL}/download", params={"url": url})
            
            await status_message.delete()
            await update.message.reply_audio(
                audio=download_response.content,
                title=info['title'],
                filename=f"{info['title']}.mp3"
            )
    except Exception as e:
        await status_message.edit_text(f"❌ Error: {str(e)}")

async def post_init(application):
    bot = application.bot
    me = await bot.get_me()
    print(f"✅ Bot logged in as @{me.username} ({me.first_name})")
    print("Bot is ready to use!")

def main():
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .connect_timeout(120)
        .read_timeout(120)
        .write_timeout(120)
        .pool_timeout(120)
        .get_updates_connect_timeout(120)
        .get_updates_read_timeout(120)
        .get_updates_write_timeout(120)
        .get_updates_pool_timeout(120)
        .build()
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Starting bot...")
    app.run_polling()

if __name__ == "__main__":
    main()
