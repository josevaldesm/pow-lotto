from aiohttp import WSCloseCode, web

from proyecto.models import LotteryState, Player

async def shutdown_handler(app: web.Application):
    state: LotteryState = app["state"]
    players: list[Player] = []
    with state.players_mutex:
        player_ids = list(state.players.keys())
        while player_ids:
            players.append(state.players.pop(player_ids.pop()))

    for player in players:
        await player.ws.close(code=WSCloseCode.GOING_AWAY, message=b"Shutdown")