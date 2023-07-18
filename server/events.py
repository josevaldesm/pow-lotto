import json
from aiohttp import WSCloseCode, web

from server.models import LotteryState, Player


async def shutdown_handler(app: web.Application):
    state: LotteryState = app["state"]
    players: list[Player] = []
    _player_ids = []
    with state.players_mutex:

        state.verdict = {}  # Cleaning verdict state
        player_ids = list(state.players.keys())
        _player_ids = list(state.players.keys())
        while player_ids:
            players.append(state.players.pop(player_ids.pop()))

    for player in players:
        await player.ws.close(code=WSCloseCode.GOING_AWAY, message=b"Shutdown")

    if state.evaluate:
        print(f"\nTimestamps per round\n\t{json.dumps([{ **log.model_dump(), 'players': _player_ids } for log in  state.ts_per_round], indent=4)}")
