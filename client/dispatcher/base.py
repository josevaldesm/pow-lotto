from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from aiohttp import WSMessage

if TYPE_CHECKING:
    from client.controller.base import Controller

class Dispatcher(ABC):

    def __init__(self):
        self.__controller: "Controller" | None = None

    @abstractmethod
    async def dispatch(self, msg: WSMessage) -> None:
        ...
    
    def attach(self, controller: "Controller"):
        self.__controller = controller

    @property
    def controller(self) -> "Controller":
        if self.__controller is None:
            raise ValueError("No controller is attached")
        
        return self.__controller