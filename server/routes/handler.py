import uuid

from aiohttp import WSCloseCode, web

from server.dispatcher import MessageDispatcher
from server.models import LotteryState
from server.messages.response import OnConnectServerMessage, LotteryStateMessageWithId


async def index_handler(request: web.Request) -> web.Response:
    return web.Response(text="Index page")


async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    dispatcher = MessageDispatcher()
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    state: LotteryState = request.app["state"]
    player_id = state.add_player(ws)
    await ws.send_json(
        data=OnConnectServerMessage(
            data=LotteryStateMessageWithId(
                round=state.round,
                k=state.difficulty,
                current_message=state.current_message,
                player_id=player_id,
            )
        ).model_dump()
    )

    try:
        async for msg in ws:
            await dispatcher.dispatch(player_id, msg, state, ws)
    finally:
        player = state.remove_player(player_id)
        if player:
            await player.ws.close(code=WSCloseCode.GOING_AWAY, message=b"Shutdown")

    return ws
