try:
    print("Testing imports...")
    import fastapi
    import uvicorn
    import yt_dlp
    import httpx
    from telegram import Update
    from telegram.ext import ApplicationBuilder
    from dotenv import load_dotenv
    print("All imports successful!")
except Exception as e:
    print(f"Import error: {e}")
