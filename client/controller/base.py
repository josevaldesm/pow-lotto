import asyncio
import aiohttp
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from client.dispatcher.base import Dispatcher

from client.messages.server import LotteryStateMessageWithId, CandidateMessage, LotteryStateMessage

class Controller(ABC):

    def __init__(self, event: asyncio.Event):
        self.event = event
        self.__ws: aiohttp.ClientWebSocketResponse | None = None
        self.__dispatcher: "Dispatcher" | None = None

    def attach(self, dispatcher: "Dispatcher") -> None:
        self.__dispatcher = dispatcher

    @property
    def dispatcher(self) -> "Dispatcher":
        if self.__dispatcher is None:
            raise ValueError("No dispatcher is attached")
        
        return self.__dispatcher

    @property
    def ws(self) -> aiohttp.ClientWebSocketResponse:
        if self.__ws is None:
            raise ValueError("Websocket connection is not set")
                
        return self.__ws
 
    async def run(self, session: aiohttp.ClientSession, url: str):
        self.dispatcher.attach(self)
        async with session.ws_connect(url) as ws:
            self.__ws = ws    
            async for msg in ws:
                await self.dispatcher.dispatch(msg)

    @abstractmethod
    async def on_connect(self, data: LotteryStateMessageWithId):
        ...

    @abstractmethod
    async def on_found_candidate(self, data: CandidateMessage):
        ...

    @abstractmethod
    async def on_lottery_message(self, data: LotteryStateMessage):
        ...