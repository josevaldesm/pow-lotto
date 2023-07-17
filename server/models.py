import uuid
import hashlib
import threading
from dataclasses import dataclass, field
from time import time

from aiohttp import web
from pydantic import BaseModel, ConfigDict

from server.utils import get_random_string


class Player(BaseModel):
    score: int
    ws: web.WebSocketResponse

    model_config = ConfigDict(arbitrary_types_allowed=True)


class PlayerLog(BaseModel):
    ts: int
    round: int 
    winner: str
    message: str
    candidate: str

class PlayerVerdict(BaseModel):
    verdict: bool

class CurrentCandidate(BaseModel):
    player_id: str
    r: str 

    def get_string(self) -> str:
        return self.player_id + self.r


@dataclass
class LotteryState:
    round: int = 0
    difficulty: int = 10
    max_rounds: int | None = None
    current_message: str = hashlib.sha256(get_random_string(32).encode()).hexdigest()
    current_candidate: CurrentCandidate | None = None
    ts_per_round: list[PlayerLog] = field(default_factory=list)
    players: dict[str, Player] = field(default_factory=dict)
    verdict: dict[str, bool] = field(default_factory=dict)
    players_mutex = threading.Lock()

    def step(self) -> None:
        if self.current_candidate is None:
            raise ValueError("Cannot step if current_candidate is None")
        
        print(f"Next round: {self.round} -> {self.round + 1}")
        winner = self.current_candidate.player_id
        player = self.players.get(winner, None)
        if player:
            player.score += 1

        self.ts_per_round.append(
            PlayerLog(
                ts=int(time()),
                round=self.round,
                winner=winner,
                message=self.current_message,
                candidate=self.current_candidate.get_string()
            )
        )
        if self.max_rounds and self.max_rounds == self.round + 1:
            print(f"Max round reached: {self.max_rounds} == {self.round + 1}")
            raise ValueError("Max round reached")
        
        self.round += 1
        self.current_message = hashlib.sha256(
            self.current_candidate.get_string().encode()
        ).hexdigest()
        self.current_candidate = None
        self.verdict = {}

    def add_player(self, ws: web.WebSocketResponse) -> str:
        with self.players_mutex:
            player_id = str(uuid.uuid4())
            self.players[player_id] = Player(ws=ws, score=0)

        return player_id

    def remove_player(self, player_id: str) -> Player | None:
        with self.players_mutex:
            self.verdict.pop(player_id, None)  # removing verdict block if exists
            return self.players.pop(player_id, None)

    def get_verdicts(self):
        return self.verdict
