# client.py
import asyncio
import aiohttp
import time

async def main():
    base_url = "http://127.0.0.1:8000"
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
