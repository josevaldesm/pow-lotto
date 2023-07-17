import json
import asyncio

from aiohttp import WSCloseCode, WSMessage, WSMsgType, web
from pydantic import ValidationError

from server.messages.handler import (
    LotteryStateRequestHandler,
    RequestHandler,
    CandidateRequestHandler,
)
from server.messages.request import PlayerRequest
from server.messages.response import ServerMessageError
from server.models import LotteryState


class MessageDispatcher:
    channel_handlers: dict[str, RequestHandler] = {
        "LOTTERY_STATE": LotteryStateRequestHandler(),
        "CANDIDATE": CandidateRequestHandler(),
    }

    async def dispatch(
        self,
        player_id: str,
        request: WSMessage,
        state: LotteryState,
        ws: web.WebSocketResponse,
    ):
        if request.type == WSMsgType.TEXT:
            try:
                parsed: dict = request.json()
            except json.JSONDecodeError as e:
                return await ws.send_json(
                    ServerMessageError(
                        type="PARSE_ERROR",
                        message="Unable to parse request into JSON",
                    ).model_dump()
                )
            return await self.__dispatch(player_id, parsed, state, ws)
        elif request.type == WSMsgType.ERROR:
            print("ws connection closed with exception %s" % ws.exception())
            player = state.remove_player(player_id)
            if player:
                await player.ws.close(code=WSCloseCode.GOING_AWAY, message=b"Shutdown")

    async def __dispatch(
        self,
        player_id: str,
        request: dict,
        state: LotteryState,
        ws: web.WebSocketResponse,
    ):
        print(f"Incoming message from {player_id}:\n \t{request}\n")
        try:
            parsed = PlayerRequest.model_validate({"request": request}).request
        except ValidationError as e:
            print(e)
            return await ws.send_json(
                ServerMessageError(
                    type="MESSAGE_ERROR",
                    message="The data you provided is invalid or channel not exist",
                ).model_dump()
            )

        handler = self.channel_handlers[parsed.channel]
        response = handler.handle(player_id, state, parsed.data)
        if not response:
            return

        if isinstance(response, ServerMessageError):
            return await ws.send_json(response.model_dump())

        with state.players_mutex:
            wss = [player.ws for player in state.players.values()]

        # Broadcast
        await asyncio.gather(*[pws.send_json(response.model_dump()) for pws in wss])
