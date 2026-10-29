import aiohttp
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def fetch(session, url):
    try:
        async with session.get(url, timeout=5) as response:
            logging.info(f"Fetching {url}... {response.status}")
            response.raise_for_status()
            return len(await response.read())
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

async def main(urls):
    semaphore = asyncio.Semaphore(2)
    results = {}

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        for task in asyncio.as_completed(tasks, limit=2):
            url = task.get_name()
            size = await task
            results[url] = size

    return results

urls = [
    "http://example.com",
    "http://example.org",
    "http://example.net",
    "http://example.edu",
    "http://example.com"
]

loop = asyncio.get_event_loop()
result = loop.run_until_complete(main(urls))
print(result)