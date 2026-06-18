import os
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

load_dotenv()

# Your bot token
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Your API URL (local or Vercel)
API_BASE_URL = os.getenv("API_BASE_URL", "https://yt-api-two-plum.vercel.app")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🎵 Hi {update.effective_user.first_name}!\n"
        "Send me any YouTube link and I'll get the audio for you!"
    )


async def handle_youtube_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Please send a valid URL!")
        return

    status_msg = await update.message.reply_text("🔍 Fetching audio info...")

    try:
        async with httpx.AsyncClient(timeout=180) as client:
            # Get info
            info_response = await client.get(f"{API_BASE_URL}/info", params={"url": url})
            if info_response.status_code != 200:
                await status_msg.edit_text("❌ Failed to get audio info!")
                return
            info = info_response.json()["data"]

            await status_msg.edit_text(f"⏳ Downloading: {info['title']}...")

            # Download
            download_response = await client.get(
                f"{API_BASE_URL}/download", params={"url": url}
            )
            if download_response.status_code != 200:
                await status_msg.edit_text("❌ Failed to download audio!")
                return

            # Send to user
            await status_msg.delete()
            await update.message.reply_audio(
                audio=download_response.content,
                title=info["title"],
                filename=f"{info['title']}.webm",  # or .mp3
            )

    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube_link)
    )

    print("✅ Bot started!")
    app.run_polling()


if __name__ == "__main__":
    main()
