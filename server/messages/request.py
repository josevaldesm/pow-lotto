from typing import Annotated, Literal

from pydantic import BaseModel, Field


class LotteryStateData(BaseModel):
    round: int
    candidate: str
    verdict: bool


class CloseData(BaseModel):
    player_id: str


class CandidateData(BaseModel):
    r: str


class VerdictData(BaseModel):
    verdict: bool


class LotteryStateRequest(BaseModel):
    channel: Literal["LOTTERY_STATE"] = "LOTTERY_STATE"
    data: LotteryStateData


class CandidateRequest(BaseModel):
    channel: Literal["CANDIDATE"] = "CANDIDATE"
    data: CandidateData


class CloseRequest(BaseModel):
    channel: Literal["CLOSE"] = "CLOSE"
    data: CloseData


Message = Annotated[
    LotteryStateRequest | CandidateRequest | CloseRequest,
    Field(discriminator="channel"),
]


class PlayerRequest(BaseModel):
    request: Message
