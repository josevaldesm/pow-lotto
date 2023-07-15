import asyncio
import json

import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect("http://localhost:8080/ws") as ws:
            async for msg in ws:
                print(msg)


if __name__ == "__main__":
    asyncio.run(main())
