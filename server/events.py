import json
from aiohttp import WSCloseCode, web

from server.models import LotteryState, Player


async def shutdown_handler(app: web.Application):
    state: LotteryState = app["state"]
    players: list[Player] = []
    with state.players_mutex:
        state.verdict = {}  # Cleaning verdict state
        player_ids = list(state.players.keys())
        while player_ids:
            players.append(state.players.pop(player_ids.pop()))

    for player in players:
        await player.ws.close(code=WSCloseCode.GOING_AWAY, message=b"Shutdown")

    print(f"\nTimestamps per round\n\t{json.dumps([log.model_dump() for log in  state.ts_per_round], indent=4)}")
