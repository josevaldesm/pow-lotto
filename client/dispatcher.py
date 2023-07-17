import json
from hashlib import sha3_256
import asyncio

from aiohttp import WSMessage, WSMsgType, ClientWebSocketResponse
from pydantic import ValidationError

from client.messages.server import ServerMessage
from client.controller import PlayerController


class ClientMessageDispatcher:
    def __init__(self, controller: PlayerController):
        self.controller = controller

    async def dispatch(
        self,
        request: WSMessage,
        ws: ClientWebSocketResponse,
    ):
        if request.type != WSMsgType.TEXT:
            return None
        try:
            msg_info = request.json()
        except json.JSONDecodeError:
            print("Unable to parse server message to JSON\nIgnoring...")
            return None
        try:
            data = ServerMessage.model_validate({"message": msg_info})
        except ValidationError:
            print(f"Unexpected message from server: {msg_info}\nIgnoring...")
            return None

        message = data.message
        if message.error is True:
            print(message.message)
            return None

        if message.channel == "ON_CONNECT":
            return await self.controller.on_connect(state=message.data, ws=ws)

        if message.channel == "CANDIDATE":
            if not self.controller.state:
                return print("State not set yet")

            await self.controller.stop_compute_task()
            vi = self.controller.state.current_message
            pid = message.data.player_id
            ri = message.data.r
            k = self.controller.state.k
            verdict = sha3_256(f"{vi}{pid}{ri}".encode()).hexdigest()[-k:] == "".join(
                ["0" for _ in range(k)]
            )
            await ws.send_json(
                {
                    "channel": "LOTTERY_STATE",
                    "data": {
                        "round": self.controller.state.round,
                        "candidate": f"{pid}{ri}",
                        "verdict": verdict,
                    },
                }
            )

        if message.channel == "LOTTERY_STATE":
            print(message.data)
            return await self.controller.on_lottery_message(state=message.data, ws=ws)
