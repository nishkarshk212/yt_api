import os
import httpx
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def test_token():
    try:
        print(f"Testing bot token...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe")
            print(f"Response status: {response.status_code}")
            print(f"Response: {response.json()}")
            if response.status_code == 200:
                print("✅ Bot token is valid!")
            else:
                print("❌ Bot token invalid!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_token())
