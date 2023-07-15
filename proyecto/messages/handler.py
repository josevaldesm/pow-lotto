from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from proyecto.messages.request import LotteryStateData
from proyecto.messages.response import (LotteryStateServerMessage, LotteryStateMessage,
                                        ServerMessage)
from proyecto.models import LotteryState

T = TypeVar("T", bound=BaseModel)


class RequestHandler(ABC, Generic[T]):
    @staticmethod
    @abstractmethod
    def handle(state: LotteryState, data: T) -> ServerMessage:
        ...


class LotteryStateRequestHandler(RequestHandler):
    @staticmethod
    def handle(state: LotteryState, data: LotteryStateData):
        # TODO: Implementar sistema de bloques
        if data.round == state.round + 1:
            state.round += 1
            state.current_message = data.current_message

            return LotteryStateServerMessage(
                data=LotteryStateMessage(
                    round=state.round,
                    k=state.difficulty,
                    current_message=state.current_message,
                )
            )
        
        return LotteryStateServerMessage(
            data=LotteryStateMessage(
                round=state.round,
                k=state.difficulty,
                current_message=state.current_message,
            )
        )
        

