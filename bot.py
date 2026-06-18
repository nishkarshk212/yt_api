import os
import yt_dlp
import tempfile
import uuid
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Simple, reliable yt-dlp options
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': False,
    'no_warnings': False,
    'noplaylist': True,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }
}

def _search_songs_sync(query: str, limit: int = 5):
    """Synchronous search function"""
    ydl_search_opts = {
        **ydl_opts,
        'extract_flat': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_search_opts) as ydl:
        results = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        return results.get('entries', [])

def _get_video_info_sync(url: str):
    """Synchronous video info function"""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info

def _download_audio_sync(url: str):
    """Synchronous download function"""
    download_dir = tempfile.mkdtemp()
    unique_id = str(uuid.uuid4())
    outtmpl = os.path.join(download_dir, f"{unique_id}.%(ext)s")
    
    download_opts = {
        **ydl_opts,
        'outtmpl': outtmpl,
    }
    
    with yt_dlp.YoutubeDL(download_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename, info

async def search_songs(query: str, limit: int = 5):
    """Async wrapper for search"""
    return await asyncio.to_thread(_search_songs_sync, query, limit)

async def get_video_info(url: str):
    """Async wrapper for video info"""
    return await asyncio.to_thread(_get_video_info_sync, url)

async def download_audio(url: str):
    """Async wrapper for download"""
    return await asyncio.to_thread(_download_audio_sync, url)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🎵 Hi {user.first_name}! 👋\n\n"
        "✅ I'm your YouTube Music Downloader Bot!\n\n"
        "📥 How to use me:\n"
        "1. Send a song name to search\n"
        "2. Or send a YouTube link directly\n\n"
        "Commands:\n"
        "• /start - Show this welcome message\n"
        "• /ping - Check if I'm alive"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏓 Pong!\n\n✅ Bot is running perfectly!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.startswith("http"):
        # Handle URL directly
        status_message = await update.message.reply_text("🔍 Fetching audio info...")

        try:
            info = await get_video_info(text)
            await status_message.edit_text(f"⏳ Downloading: {info['title']}...")
            
            audio_file, info = await download_audio(text)
            
            await status_message.delete()
            with open(audio_file, 'rb') as f:
                await update.message.reply_audio(
                    audio=f,
                    title=info['title'],
                    filename=f"{info['title']}.{info['ext']}",
                )
            
            # Clean up
            os.remove(audio_file)
            os.rmdir(os.path.dirname(audio_file))
            
        except Exception as e:
            await status_message.edit_text(f"❌ Error: {str(e)}")
    else:
        # Search for song
        status_message = await update.message.reply_text("🔍 Searching for songs...")

        try:
            results = await search_songs(text, limit=5)
            
            if not results:
                await status_message.edit_text("❌ No results found!")
                return

            # Create inline keyboard
            keyboard = []
            for i, song in enumerate(results):
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"{i+1}. {song['title'][:50]}...",
                            callback_data=f"download:{song['url']}",
                        )
                    ]
                )

            reply_markup = InlineKeyboardMarkup(keyboard)

            await status_message.delete()
            await update.message.reply_text(
                "🎵 Here are the results! Choose one to download:",
                reply_markup=reply_markup,
            )
        except Exception as e:
            await status_message.edit_text(f"❌ Error: {str(e)}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("download:"):
        url = query.data.split(":", 1)[1]

        status_message = await query.message.reply_text("🔍 Fetching audio info...")

        try:
            info = await get_video_info(url)
            await status_message.edit_text(f"⏳ Downloading: {info['title']}...")
            
            audio_file, info = await download_audio(url)
            
            await status_message.delete()
            with open(audio_file, 'rb') as f:
                await query.message.reply_audio(
                    audio=f,
                    title=info['title'],
                    filename=f"{info['title']}.{info['ext']}",
                )
            
            # Clean up
            os.remove(audio_file)
            os.rmdir(os.path.dirname(audio_file))
            
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
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("Starting bot...")
    app.run_polling()

if __name__ == "__main__":
    main()