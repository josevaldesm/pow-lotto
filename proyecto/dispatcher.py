import json

from aiohttp import WSCloseCode, WSMessage, WSMsgType, web
from pydantic import ValidationError

from proyecto.messages.handler import LotteryStateRequestHandler, RequestHandler
from proyecto.messages.request import PlayerRequest
from proyecto.messages.response import ServerMessageError
from proyecto.models import LotteryState


class MessageDispatcher:
    channel_handlers: dict[str, RequestHandler] = {"LOTTERY_STATE": LotteryStateRequestHandler()}

    async def dispatch(self, player_id: str, request: WSMessage, state: LotteryState, ws: web.WebSocketResponse):
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
            return await self.__dispatch(parsed, state, ws)
        elif request.type == WSMsgType.ERROR:
            print("ws connection closed with exception %s" % ws.exception())
            player = state.remove_player(player_id)
            if player:
                await player.ws.close(code=WSCloseCode.GOING_AWAY, message=b"Shutdown")

    async def __dispatch(
        self, request: dict, state: LotteryState, ws: web.WebSocketResponse
    ):
        try:
            parsed = PlayerRequest.model_validate({"request": request}).request
        except ValidationError:
            return await ws.send_json(
                ServerMessageError(
                    type="MESSAGE_ERROR",
                    message="The data you provided is invalid or channel not exist",
                ).model_dump()
            )

        handler = self.channel_handlers[parsed.channel]
        response = handler.handle(state, parsed.data)
        return await ws.send_json(response.model_dump())
