import asyncio

import aiohttp


from client.dispatcher.ws import ClientMessageDispatcher
from client.controller.player import PlayerController


async def main():
    event = asyncio.Event()
    loop = asyncio.get_event_loop()
    controller = PlayerController(event=event)
    controller.attach(ClientMessageDispatcher())
    async with aiohttp.ClientSession(loop=loop) as session:
        await controller.run(session, "http://localhost:8080/ws")

if __name__ == "__main__":
    asyncio.run(main())
