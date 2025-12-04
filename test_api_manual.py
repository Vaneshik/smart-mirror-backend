#!/usr/bin/env python3
"""
Простой скрипт для ручного тестирования API
Запустите сервер (make run) и запустите этот скрипт
"""
import asyncio
import httpx


BASE_URL = "http://localhost:8000"


async def test_health():
    """Test health endpoints"""
    print("=" * 50)
    print("Testing Health Checks")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Main health
        response = await client.get(f"{BASE_URL}/health")
        print(f"✓ Main health: {response.json()}")
        
        # LLM health
        response = await client.get(f"{BASE_URL}/api/llm/health")
        print(f"✓ LLM health: {response.json()}")
        
        # Music health
        response = await client.get(f"{BASE_URL}/api/music/health")
        print(f"✓ Music health: {response.json()}")
    
    print()


async def test_llm():
    """Test LLM query"""
    print("=" * 50)
    print("Testing LLM")
    print("=" * 50)
    
    queries = [
        "Привет, как дела?",
        "Расскажи анекдот",
        "Какая сегодня погода?"
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for query in queries:
            print(f"\nQuery: {query}")
            try:
                response = await client.post(
                    f"{BASE_URL}/api/llm/query",
                    json={"text": query}
                )
                result = response.json()
                print(f"Response: {result['response'][:100]}...")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print()


async def test_music():
    """Test music search and stream"""
    print("=" * 50)
    print("Testing Music")
    print("=" * 50)
    
    search_queries = ["Metallica", "Imagine Dragons", "Любэ"]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for query in search_queries:
            print(f"\nSearching: {query}")
            try:
                # Search
                response = await client.get(
                    f"{BASE_URL}/api/music/search",
                    params={"q": query}
                )
                result = response.json()
                print(f"Found {result['total']} tracks")
                
                # Get stream URL for first track
                if result['tracks']:
                    track = result['tracks'][0]
                    print(f"  Track: {track['artist']} - {track['title']}")
                    
                    stream_response = await client.get(
                        f"{BASE_URL}/api/music/track/{track['id']}/stream"
                    )
                    stream_url = stream_response.json()['stream_url']
                    print(f"  ✓ Stream URL obtained: {stream_url[:50]}...")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print()


async def main():
    """Run all tests"""
    print("\n🚀 Starting API Tests\n")
    
    try:
        await test_health()
        await test_llm()
        await test_music()
        
        print("=" * 50)
        print("✅ All tests completed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())

