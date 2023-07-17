from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from server.messages.request import LotteryStateData, CandidateData
from server.messages.response import (
    LotteryStateServerMessage,
    CandidateMessage,
    CandidateServerMessage,
    LotteryStateMessage,
    ServerMessage,
    ServerMessageError,
)
from server.models import LotteryState, PlayerVerdict

T = TypeVar("T", bound=BaseModel)


class RequestHandler(ABC, Generic[T]):
    @staticmethod
    @abstractmethod
    def handle(player_id: str, state: LotteryState, data: T) -> ServerMessage | None:
        ...


class CandidateRequestHandler(RequestHandler[CandidateData]):

    @staticmethod
    def handle(player_id: str, state: LotteryState, data: CandidateData):
        with state.players_mutex:
            if state.verdict is not None:
                return ServerMessageError(
                    type="VERDICT_ALREADY_SET",
                    message="Attempt to send a candidate where players are verdicting"
                )

            state.verdict = {}

        return CandidateServerMessage(
            data=CandidateMessage(
                r=data.r,
                player_id=player_id
            )
        )

class LotteryStateRequestHandler(RequestHandler[LotteryStateData]):
    @staticmethod
    def handle(player_id: str, state: LotteryState, data: LotteryStateData):
        with state.players_mutex:
            if state.verdict is None:
                return ServerMessageError(
                    type="VERDICT_NOT_SET",
                    message="Attempt to send a verdict where no player send a candidate before",
                )

            if state.verdict.get(player_id, None) != None:
                return ServerMessageError(
                    type="VERDICT_ALREADY_SENT",
                    message="There already exists a verdict for current round",
                )

            state.verdict[player_id] = PlayerVerdict(
                round=state.round, candidate=data.candidate, verdict=data.verdict
            )

            n_players = len(state.players)
            blocks = state.get_current_round_blocks()

            print(f"n_players: {n_players}\nblocks={blocks}")
            if (
                len(blocks) < n_players / 2
            ):  # At least 50% of players must to send a verdict
                print("Waiting verdict for other players")
                return None

            agreeded = len(list(filter(lambda block: block.verdict, blocks)))
            print(f"agreeded: {agreeded}")
            if agreeded >= len(blocks):  # all verdict are true
                print(f"Stepping round from {state.round} to {state.round + 1}")
                state.step(blocks[0].candidate)
                return LotteryStateServerMessage(
                    data=LotteryStateMessage(
                        round=state.round,
                        k=state.difficulty,
                        current_message=state.current_message,
                    )
                )

            # Go back to current round
            return LotteryStateServerMessage(
                data=LotteryStateMessage(
                    round=state.round,
                    k=state.difficulty,
                    current_message=state.current_message,
                )
            )
