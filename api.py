from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
import yt_dlp
import os
import tempfile
import uuid
import httpx
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import static_ffmpeg

load_dotenv()

# Add static ffmpeg paths
static_ffmpeg.add_paths()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

app = FastAPI(title="YT-DLP Music API")

DOWNLOAD_DIR = tempfile.mkdtemp()
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
    'quiet': True,
    'no_warnings': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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

@app.get("/download")
async def download_audio(url: str = Query(..., description="YouTube or video URL")):
    file_id = str(uuid.uuid4())
    temp_opts = ydl_opts.copy()
    temp_opts['outtmpl'] = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")
    
    try:
        with yt_dlp.YoutubeDL(temp_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            mp3_path = os.path.splitext(file_path)[0] + ".mp3"
            
            if os.path.exists(mp3_path):
                return FileResponse(mp3_path, media_type="audio/mpeg", filename=f"{info['title']}.mp3")
            else:
                raise HTTPException(status_code=500, detail="Failed to convert to MP3")
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
                    "📥 Just send me any YouTube (or other supported site) link and I'll send you the audio in MP3 format!\n\n"
                    "Commands:\n"
                    "• /start - Show this welcome message\n"
                    "• /check - Check if I'm alive"
                )
                return {"status": "success"}
            
            elif text.startswith("/check"):
                await send_telegram_message(chat_id, "🏓 Pong!\n\n✅ Bot is running perfectly!")
                return {"status": "success"}
            
            # Handle text messages (URLs)
            elif text.startswith("http"):
                status_msg = await send_telegram_message(chat_id, "🔍 Fetching audio info...")
                
                try:
                    # Get audio info
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(text, download=False)
                    
                    await send_telegram_message(chat_id, f"⏳ Downloading: {info['title']}...")
                    
                    # Download and convert
                    file_id = str(uuid.uuid4())
                    temp_opts = ydl_opts.copy()
                    temp_opts['outtmpl'] = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")
                    
                    with yt_dlp.YoutubeDL(temp_opts) as ydl:
                        info = ydl.extract_info(text, download=True)
                        file_path = ydl.prepare_filename(info)
                        mp3_path = os.path.splitext(file_path)[0] + ".mp3"
                    
                    if os.path.exists(mp3_path):
                        with open(mp3_path, "rb") as f:
                            await send_telegram_audio(chat_id, f, info['title'])
                    
                    return {"status": "success", "message": "Audio sent!"}
                
                except Exception as e:
                    await send_telegram_message(chat_id, f"❌ Error: {str(e)}")
                    return {"status": "error", "message": str(e)}
            else:
                await send_telegram_message(chat_id, "❌ Please send a valid URL starting with http:// or https://")
                return {"status": "error"}
        
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
