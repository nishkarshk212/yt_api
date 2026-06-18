from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import yt_dlp
import os
import tempfile
import uuid
from typing import Optional

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
}

@app.get("/")
async def root():
    return {"message": "YT-DLP Music API"}

@app.get("/info/{url:path}")
async def get_audio_info(url: str):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "id": info.get("id"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
                "url": url
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{url:path}")
async def download_audio(url: str):
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
