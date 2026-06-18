import httpx

async def test_vercel_api():
    vercel_url = "https://yt-api-two-plum.vercel.app"
    test_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        print(f"🔍 Testing Vercel API at {vercel_url}...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Test root endpoint
            root_response = await client.get(f"{vercel_url}/")
            print(f"✅ Root endpoint: {root_response.status_code} - {root_response.json()}")
            
            # Test info endpoint
            info_response = await client.get(f"{vercel_url}/info/{test_video_url}")
            print(f"✅ Info endpoint: {info_response.status_code}")
            if info_response.status_code == 200:
                info = info_response.json()
                print(f"  - Title: {info['title']}")
                print(f"  - Duration: {info['duration']}s")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_vercel_api())
