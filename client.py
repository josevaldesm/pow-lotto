import asyncio

import aiohttp


from client.dispatcher import ClientMessageDispatcher
from client.controller import PlayerController


async def main():
    event = asyncio.Event()
    loop = asyncio.get_running_loop()
    controller = PlayerController(event=event)
    dispatcher = ClientMessageDispatcher(controller=controller)
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect("http://localhost:8080/ws") as ws:
            async for msg in ws:
                await dispatcher.dispatch(msg, ws)


if __name__ == "__main__":
    asyncio.run(main())
