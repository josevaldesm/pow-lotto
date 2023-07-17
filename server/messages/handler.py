import os
import signal
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
from server.models import LotteryState, CurrentCandidate

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
            if state.current_candidate is not None:
                return ServerMessageError(
                    type="VERDICT_ALREADY_SET",
                    message=f"Player {player_id} attempted to send a candidate where players are verdicting",
                    data={ "r": state.current_candidate.r, "player_id": state.current_candidate.player_id }
                )

            state.current_candidate = CurrentCandidate(player_id=player_id, r=data.r)

        return CandidateServerMessage(
            data=CandidateMessage(r=data.r, player_id=player_id)
        )


class LotteryStateRequestHandler(RequestHandler[LotteryStateData]):
    @staticmethod
    def handle(player_id: str, state: LotteryState, data: LotteryStateData):
        with state.players_mutex:
            if state.current_candidate is None:
                return ServerMessageError(
                    type="VERDICT_NOT_SET",
                    message=f"Player {player_id} attempted to send a verdict where no player send a candidate before",
                    data=LotteryStateMessage(
                        round=state.round,
                        k=state.difficulty,
                        current_message=state.current_message,
                    ).model_dump()
                )

            if state.verdict.get(player_id, None) != None:
                return ServerMessageError(
                    type="VERDICT_ALREADY_SENT",
                    message=f"Player {player_id} sent a verdict for same round twice",
                )

            if data.candidate != state.current_candidate.get_string():
                return ServerMessageError(
                    type="INVALID_VERDICT",
                    message=f"Player {player_id} sent a verdict with a different candidate",
                )

            state.verdict[player_id] = data.verdict

            n_players = len(state.players)
            verdicts = state.get_verdicts()

            if (len(verdicts) < n_players):  
                print("Waiting for more players until decide")
                return None
            
            agreeded = len(list(filter(lambda agreeded: agreeded, verdicts.values())))
            if agreeded >= len(verdicts) / 2:  # 50 % of verdict are true
                try:
                    state.step()
                    return LotteryStateServerMessage(
                        data=LotteryStateMessage(
                            round=state.round,
                            k=state.difficulty,
                            current_message=state.current_message,
                        )
                    )
                except ValueError:
                    os.kill(os.getpid(), signal.SIGINT)
                    return None

            print(f"There is no consensus over player {state.current_candidate.player_id} candidate, restarting round")
            return LotteryStateServerMessage(
                data=LotteryStateMessage(
                    round=state.round,
                    k=state.difficulty,
                    current_message=state.current_message,
                )
            )
