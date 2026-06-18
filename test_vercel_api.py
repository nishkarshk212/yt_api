import httpx

async def test_vercel_api():
    vercel_url = "https://yt-api-two-plum.vercel.app"
    test_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    output_file = "vercel_test_audio.mp3"
    
    try:
        print(f"🔍 Testing Vercel API at {vercel_url}...")
        async with httpx.AsyncClient(timeout=180.0) as client:
            # Test root endpoint
            root_response = await client.get(f"{vercel_url}/")
            print(f"✅ Root endpoint: {root_response.status_code} - {root_response.json()}")
            
            # Test check endpoint
            check_response = await client.get(f"{vercel_url}/check")
            print(f"✅ Check endpoint: {check_response.status_code} - {check_response.json()}")
            
            # Test info endpoint with query param
            info_response = await client.get(f"{vercel_url}/info", params={"url": test_video_url})
            print(f"✅ Info endpoint: {info_response.status_code}")
            if info_response.status_code == 200:
                info = info_response.json()
                print(f"  - Title: {info['data']['title']}")
                print(f"  - Duration: {info['data']['duration']}s")
            else:
                print(f"❌ Info error: {info_response.text}")
            
            # Test download endpoint with query param
            print("⏳ Downloading audio from Vercel...")
            download_response = await client.get(f"{vercel_url}/download", params={"url": test_video_url})
            print(f"✅ Download endpoint: {download_response.status_code}")
            
            if download_response.status_code == 200:
                with open(output_file, "wb") as f:
                    f.write(download_response.content)
                print(f"✅ Audio saved as {output_file} ({len(download_response.content)} bytes)")
            else:
                print(f"❌ Download error: {download_response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_vercel_api())
