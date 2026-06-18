from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
import yt_dlp
import os
import tempfile
import uuid
import httpx
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

app = FastAPI(title="YT-DLP Music API")

DOWNLOAD_DIR = tempfile.mkdtemp()
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Options without postprocessor (no ffmpeg needed for info)
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
    'quiet': True,
    'no_warnings': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'geo_bypass': True,
    'geo_bypass_country': 'US',
    'socket_timeout': 30,
    'retries': 10,
    'fragment_retries': 10,
    'extractor_retries': 10,
    'noplaylist': True,
    'write_pages': False,
    'writeinfojson': False,
    'postprocessor_args': {
        'ffmpeg_i': ['-nostdin'],
    },
}

async def send_telegram_message(chat_id: int, text: str):
    """Send a text message to Telegram chat."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        await client.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": text}
        )

async def send_telegram_audio(chat_id: int, audio_file, title: str):
    """Send an audio file to Telegram chat."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        files = {"audio": (f"{title}.mp3", audio_file)}
        await client.post(
            f"{TELEGRAM_API_URL}/sendAudio",
            data={"chat_id": chat_id, "title": title},
            files=files
        )

@app.get("/")
async def root():
    return {"message": "YT-DLP Music API"}

@app.get("/check")
async def check():
    return {"status": "success", "message": "API is running!"}

@app.get("/info")
async def get_audio_info(url: str = Query(..., description="YouTube or video URL")):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "status": "success",
                "data": {
                    "title": info.get("title"),
                    "id": info.get("id"),
                    "duration": info.get("duration"),
                    "thumbnail": info.get("thumbnail"),
                    "url": url
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})

@app.get("/search")
async def search_songs(query: str = Query(..., description="Search query (song name, artist, etc.)"), limit: int = Query(5, description="Number of results to return")):
    try:
        search_opts = ydl_opts.copy()
        search_opts['quiet'] = True
        search_opts['extract_flat'] = True
        
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            # Use yt-dlp's YouTube search
            results = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            
            if not results or 'entries' not in results:
                raise HTTPException(status_code=404, detail="No results found")
            
            # Format the results
            songs = []
            for entry in results['entries']:
                if entry:  # Skip None entries
                    songs.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                        'duration': entry.get('duration'),
                        'thumbnail': entry.get('thumbnail'),
                        'channel': entry.get('channel')
                    })
            
            return {
                'status': 'success',
                'query': query,
                'results': songs
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download")
async def download_audio(url: str = Query(..., description="YouTube or video URL")):
    file_id = str(uuid.uuid4())
    temp_opts = ydl_opts.copy()
    temp_opts['outtmpl'] = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")
    
    try:
        with yt_dlp.YoutubeDL(temp_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            if os.path.exists(file_path):
                # Determine the correct media type
                ext = os.path.splitext(file_path)[1].lower()
                media_type = "audio/mpeg" if ext == ".mp3" else "audio/webm" if ext == ".webm" else "audio/*"
                filename = f"{info['title']}{ext}"
                return FileResponse(file_path, media_type=media_type, filename=filename)
            else:
                raise HTTPException(status_code=500, detail="Failed to download audio")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        update: Dict[str, Any] = await request.json()
        
        if "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            
            # Handle commands
            if text.startswith("/start"):
                first_name = message["from"].get("first_name", "User")
                await send_telegram_message(
                    chat_id,
                    f"🎵 Hi {first_name}! 👋\n\n"
                    "✅ I'm your YouTube Music Downloader Bot!\n\n"
                    "📥 How to use me:\n"
                    "1. Send a song name to search\n"
                    "2. Or send a YouTube link directly\n\n"
                    "Commands:\n"
                    "• /start - Show this welcome message\n"
                    "• /check - Check if I'm alive"
                )
                return {"status": "success"}
            
            elif text.startswith("/check"):
                await send_telegram_message(chat_id, "🏓 Pong!\n\n✅ Bot is running perfectly!")
                return {"status": "success"}
            
            # Handle text messages
            elif text.startswith("http"):
                # Handle URL directly
                status_msg = await send_telegram_message(chat_id, "🔍 Fetching audio info...")
                
                try:
                    # Get audio info
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(text, download=False)
                    
                    await send_telegram_message(chat_id, f"⏳ Downloading: {info['title']}...")
                    
                    # Download
                    file_id = str(uuid.uuid4())
                    temp_opts = ydl_opts.copy()
                    temp_opts['outtmpl'] = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")
                    
                    with yt_dlp.YoutubeDL(temp_opts) as ydl:
                        info = ydl.extract_info(text, download=True)
                        file_path = ydl.prepare_filename(info)
                    
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            await send_telegram_audio(chat_id, f, info['title'])
                    
                    return {"status": "success", "message": "Audio sent!"}
                
                except Exception as e:
                    await send_telegram_message(chat_id, f"❌ Error: {str(e)}")
                    return {"status": "error", "message": str(e)}
            else:
                # Search for song
                status_msg = await send_telegram_message(chat_id, "🔍 Searching for songs...")
                
                try:
                    search_opts = ydl_opts.copy()
                    search_opts['quiet'] = True
                    search_opts['extract_flat'] = True
                    
                    with yt_dlp.YoutubeDL(search_opts) as ydl:
                        results = ydl.extract_info(f"ytsearch5:{text}", download=False)
                    
                    if not results or 'entries' not in results:
                        await send_telegram_message(chat_id, "❌ No results found!")
                        return {"status": "error"}
                    
                    # Prepare inline keyboard
                    keyboard = []
                    for i, entry in enumerate(results['entries']):
                        if entry:
                            keyboard.append([{
                                "text": f"{i+1}. {entry.get('title', 'Unknown')[:50]}...",
                                "callback_data": f"download:{entry.get('id')}"
                            }])
                    
                    # Send search results
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        await client.post(
                            f"{TELEGRAM_API_URL}/sendMessage",
                            json={
                                "chat_id": chat_id,
                                "text": "🎵 Here are the results! Choose one to download:",
                                "reply_markup": {
                                    "inline_keyboard": keyboard
                                }
                            }
                        )
                    
                    return {"status": "success"}
                
                except Exception as e:
                    await send_telegram_message(chat_id, f"❌ Error: {str(e)}")
                    return {"status": "error", "message": str(e)}
        
        # Handle callback queries (when user selects a song)
        elif "callback_query" in update:
            callback_query = update["callback_query"]
            chat_id = callback_query["message"]["chat"]["id"]
            data = callback_query.get("data", "")
            
            if data.startswith("download:"):
                video_id = data.split(":", 1)[1]
                url = f"https://www.youtube.com/watch?v={video_id}"
                
                # Answer callback query
                async with httpx.AsyncClient(timeout=60.0) as client:
                    await client.post(
                        f"{TELEGRAM_API_URL}/answerCallbackQuery",
                        json={"callback_query_id": callback_query["id"]}
                    )
                
                # Download and send
                status_msg = await send_telegram_message(chat_id, "⏳ Downloading...")
                
                try:
                    # Get audio info
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                    
                    await send_telegram_message(chat_id, f"⏳ Downloading: {info['title']}...")
                    
                    # Download
                    file_id = str(uuid.uuid4())
                    temp_opts = ydl_opts.copy()
                    temp_opts['outtmpl'] = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")
                    
                    with yt_dlp.YoutubeDL(temp_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        file_path = ydl.prepare_filename(info)
                    
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            await send_telegram_audio(chat_id, f, info['title'])
                    
                    return {"status": "success", "message": "Audio sent!"}
                
                except Exception as e:
                    await send_telegram_message(chat_id, f"❌ Error: {str(e)}")
                    return {"status": "error", "message": str(e)}
        
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
