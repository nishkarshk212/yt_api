import httpx

API_BASE = "http://localhost:8000"

async def test_api():
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    async with httpx.AsyncClient() as client:
        # Test info endpoint
        info_response = await client.get(f"{API_BASE}/info/{test_url}")
        print("Info response status:", info_response.status_code)
        if info_response.status_code == 200:
            print("Info:", info_response.json())

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_api())
