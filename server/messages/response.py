from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class LotteryStateMessage(BaseModel):
    round: int
    k: int
    current_message: str


class LotteryStateMessageWithId(LotteryStateMessage):
    player_id: str


class CandidateMessage(BaseModel):
    r: str
    player_id: str


class ServerMessageError(BaseModel, Generic[T]):
    error: Literal[True] = True
    type: str
    message: str


class ServerMessageSuccess(BaseModel, Generic[T]):
    data: T
    channel: str
    error: Literal[False] = False


class LotteryStateServerMessage(ServerMessageSuccess[LotteryStateMessage]):
    channel: Literal["LOTTERY_STATE"] = "LOTTERY_STATE"


class OnConnectServerMessage(ServerMessageSuccess[LotteryStateMessageWithId]):
    channel: Literal["ON_CONNECT"] = "ON_CONNECT"


class CandidateServerMessage(ServerMessageSuccess[CandidateMessage]):
    channel: Literal["CANDIDATE"] = "CANDIDATE"


ServerMessage = Annotated[
    ServerMessageSuccess | ServerMessageError, Field(discriminator="error")
]
