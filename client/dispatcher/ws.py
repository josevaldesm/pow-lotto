import json

from aiohttp import WSMsgType, WSMessage
from pydantic import ValidationError

from client.messages.server import ServerMessage, ServerMessage, CandidateMessage, LotteryStateMessage
from client.dispatcher.base import Dispatcher

class ClientMessageDispatcher(Dispatcher):
    @staticmethod
    def parse_request(request: WSMessage) -> ServerMessage |  None:
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

        return data

    async def dispatch(
        self,
        msg: WSMessage,
    ):
        if self.controller is None:
            raise ValueError("No controller is attached to this dispatcher")
        
        request = self.parse_request(msg)
        if not request: return None

        message = request.message
        if message.error is True:
            if message.type == "VERDICT_ALREADY_SET":
                # Player sent a candidate in verdict state, force player to verdict
                if message.data is None: # No me alcanza el tiempo para hacer el sistema de tipos :(
                    raise ValueError("never")
                
                await self.controller.on_found_candidate(data=CandidateMessage(
                    r=message.data["r"],
                    player_id=message.data["player_id"]
                )) 
            elif message.type == "VERDICT_NOT_SET":
                # Player is unsyncronized because it send a verdict where players are computing
                if message.data is None: # No me alcanza el tiempo para hacer el sistema de tipos :(
                    raise ValueError("never")
                
                await self.controller.on_lottery_message(data=LotteryStateMessage(
                    round=message.data["round"],
                    k=message.data["k"],
                    current_message=message.data["current_message"]
                ))
            else: 
                print(message.message)
       
        else:
            if message.channel == "ON_CONNECT":
                await self.controller.on_connect(data=message.data)

            elif message.channel == "CANDIDATE":
                await self.controller.on_found_candidate(data=message.data)

            elif message.channel == "LOTTERY_STATE":
                await self.controller.on_lottery_message(data=message.data)