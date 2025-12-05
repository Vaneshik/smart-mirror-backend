#!/usr/bin/env python3
"""
Тестирование всех функций MVP
"""
import asyncio
import httpx
import time


BASE_URL = "http://localhost:8000"


async def test_health():
    """Test health check"""
    print("=" * 60)
    print("🏥 Testing Health Check")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"✓ Status: {response.status_code}")
        print(f"  Response: {response.json()}")
    print()


async def test_llm_short_response():
    """Test LLM with short response (150 tokens limit)"""
    print("=" * 60)
    print("🤖 Testing LLM (короткие ответы для колонки)")
    print("=" * 60)
    
    queries = [
        "Привет, как дела?",
        "Расскажи анекдот",
        "Что такое черная дыра?",
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, query in enumerate(queries, 1):
            print(f"\n{i}. Query: {query}")
            try:
                start = time.time()
                response = await client.post(
                    f"{BASE_URL}/api/llm/query",
                    json={"text": query}
                )
                elapsed = time.time() - start
                
                result = response.json()
                answer = result['response']
                word_count = len(answer.split())
                
                print(f"   ✓ Response ({elapsed:.2f}s, {word_count} слов):")
                print(f"   {answer}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    print()


async def test_rate_limiting():
    """Test rate limiting (10 LLM requests per minute)"""
    print("=" * 60)
    print("⏱️  Testing Rate Limiting (10 LLM запросов/мин)")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\nОтправляю 12 запросов подряд...")
        
        for i in range(1, 13):
            try:
                response = await client.post(
                    f"{BASE_URL}/api/llm/query",
                    json={"text": f"Тест {i}"}
                )
                
                if response.status_code == 200:
                    print(f"  {i}. ✓ Success (200)")
                elif response.status_code == 429:
                    print(f"  {i}. 🛑 Rate limited (429)")
                    print(f"     {response.json()['detail']}")
                    break
                    
            except Exception as e:
                print(f"  {i}. ❌ Error: {e}")
                
            await asyncio.sleep(0.1)  # Small delay between requests
    print()


async def test_music():
    """Test music search and stream"""
    print("=" * 60)
    print("🎵 Testing Yandex Music")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Search
        print("\n1. Поиск музыки: 'Metallica'")
        try:
            response = await client.get(
                f"{BASE_URL}/api/music/search",
                params={"q": "Metallica"}
            )
            result = response.json()
            print(f"   ✓ Найдено: {result['total']} треков")
            
            if result['tracks']:
                track = result['tracks'][0]
                print(f"   Первый трек: {track['artist']} - {track['title']}")
                
                # Get stream URL
                print(f"\n2. Получение stream URL для трека {track['id']}")
                stream_response = await client.get(
                    f"{BASE_URL}/api/music/track/{track['id']}/stream"
                )
                stream_url = stream_response.json()['stream_url']
                print(f"   ✓ Stream URL получен: {stream_url[:60]}...")
                print(f"\n   💡 Для воспроизведения:")
                print(f"      mpv \"{stream_url}\"")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    print()


async def test_fallback():
    """Test fallback mechanism (needs wrong primary key)"""
    print("=" * 60)
    print("🔄 Testing Fallback Mechanism")
    print("=" * 60)
    print("(Для полного теста нужно временно указать неверный primary ключ)")
    print("Сейчас должен работать primary (artemox)")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            start = time.time()
            response = await client.post(
                f"{BASE_URL}/api/llm/query",
                json={"text": "Проверка провайдера"}
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                print(f"✓ Ответ получен за {elapsed:.2f}s")
                print("  (Проверьте логи сервера чтобы увидеть какой провайдер сработал)")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()


async def main():
    """Run all tests"""
    print("\n🚀 SmartMirror Backend - Тестирование MVP\n")
    
    try:
        await test_health()
        await test_llm_short_response()
        await test_music()
        await test_rate_limiting()
        await test_fallback()
        
        print("=" * 60)
        print("✅ Все тесты завершены!")
        print("=" * 60)
        print("\n💡 Следите за логами сервера для подробностей:")
        print("   journalctl -u smartmirror -f")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())

