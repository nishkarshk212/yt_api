import httpx
import asyncio

async def test_search():
    base_url = "http://localhost:8000"
    test_query = "Never Gonna Give You Up"
    
    print(f"🔍 Testing search for '{test_query}'...")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Test root
        root = await client.get(base_url + "/")
        print(f"Root: {root.status_code}")
        
        # Test search
        response = await client.get(base_url + "/search", params={"query": test_query, "limit": 3})
        print(f"Search status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nFound {len(data['results'])} results:")
            for i, song in enumerate(data['results']):
                print(f"\n{i+1}. {song['title']}")
                print(f"   URL: {song['url']}")
                print(f"   Channel: {song.get('channel', 'Unknown')}")
                print(f"   Duration: {song.get('duration')} seconds")

if __name__ == "__main__":
    asyncio.run(test_search())
