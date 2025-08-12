# client.py
import asyncio
import aiohttp
import time

async def fetch(session, url, request_id):
    start_time = time.time()
    try:
        async with session.get(url) as response:
            res = await response.json()
            end_time = time.time()
            duration = end_time - start_time
            print(f"Request {request_id} | Status: {response.status} | Time: {duration:.2f}s | Response: {res['message']}")
            return response.status
    except aiohttp.ClientError as e:
        print(f"Request {request_id} | Error: {e}")
        return None

async def main():
    base_url = "http://127.0.0.1:8000"
    
    # First, make a blocking request to occupy one worker
    # print("Sending blocking request to /blocked...")
    # async with aiohttp.ClientSession() as session:
    #    await fetch(session, f"{base_url}/blocked?id=1", 1)

    print("\nSimulating 1 req to blocked and 9 concurrent requests to the unblocked endpoint...")
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(11):
            if i == 0:
                print("Sending blocking request to /blocked...")
                tasks.append(fetch(session, f"{base_url}/blocked?id={i}", i))
            else:
                tasks.append(fetch(session, f"{base_url}/unblocked?id={i}", i))
        
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())