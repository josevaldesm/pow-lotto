from aiohttp import WSCloseCode, web

from proyecto.models import LotteryState


async def shutdown_handler(app: web.Application):
    state: LotteryState = app["state"]

    for player in set(state.players.values()):
        await player.ws.close(code=WSCloseCode.GOING_AWAY, message=b"Shutdown")
