from typing import TypeVar, Generic, Literal, Annotated

from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)
C = TypeVar("C")


class LotteryStateMessage(BaseModel):
    round: int
    k: int
    current_message: str


class LotteryStateMessageWithId(LotteryStateMessage):
    player_id: str


class CandidateMessage(BaseModel):
    r: str
    player_id: str


class ServerMessageSuccess(BaseModel, Generic[T]):
    channel: str
    data: T
    error: Literal[False] = False


class LotteryStateServerMessage(ServerMessageSuccess[LotteryStateMessage]):
    channel: Literal["LOTTERY_STATE"] = "LOTTERY_STATE"


class OnConnectServerMessage(ServerMessageSuccess[LotteryStateMessageWithId]):
    channel: Literal["ON_CONNECT"] = "ON_CONNECT"


class CandidateServerMessage(ServerMessageSuccess[CandidateMessage]):
    channel: Literal["CANDIDATE"] = "CANDIDATE"


class ServerMessageError(BaseModel):
    error: Literal[True] = True
    type: str
    message: str


MessageSuccess = Annotated[
    LotteryStateServerMessage | OnConnectServerMessage | CandidateServerMessage,
    Field(discriminator="channel"),
]
Message = Annotated[MessageSuccess | ServerMessageError, Field(discriminator="error")]


class ServerMessage(BaseModel):
    message: Message
