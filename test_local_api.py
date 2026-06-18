import httpx
import os

async def test_local_api():
    local_url = "http://localhost:8000"
    test_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    output_file_base = "test_audio"
    
    try:
        print(f"🔍 Testing Local API at {local_url}...")
        async with httpx.AsyncClient(timeout=180.0) as client:
            # Test root endpoint
            root_response = await client.get(f"{local_url}/")
            print(f"✅ Root endpoint: {root_response.status_code} - {root_response.json()}")
            
            # Test check endpoint
            check_response = await client.get(f"{local_url}/check")
            print(f"✅ Check endpoint: {check_response.status_code} - {check_response.json()}")
            
            # Test info endpoint with query param
            info_response = await client.get(f"{local_url}/info", params={"url": test_video_url})
            print(f"✅ Info endpoint: {info_response.status_code}")
            if info_response.status_code == 200:
                info = info_response.json()
                print(f"  - Title: {info['data']['title']}")
                print(f"  - Duration: {info['data']['duration']}s")
            
            # Test download endpoint with query param
            print("⏳ Downloading audio...")
            download_response = await client.get(f"{local_url}/download", params={"url": test_video_url})
            print(f"✅ Download endpoint: {download_response.status_code}")
            
            if download_response.status_code == 200:
                # Determine extension from content-type
                content_type = download_response.headers.get("content-type", "")
                ext = ".webm" if "webm" in content_type else ".mp3"
                output_file = f"{output_file_base}{ext}"
                
                with open(output_file, "wb") as f:
                    f.write(download_response.content)
                print(f"✅ Audio saved as {output_file} ({len(download_response.content)} bytes)")
            else:
                print(f"❌ Download error: {download_response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_local_api())

