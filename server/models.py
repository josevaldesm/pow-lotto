import uuid
import hashlib
import threading
from dataclasses import dataclass, field

from aiohttp import web
from pydantic import BaseModel, ConfigDict

from server.utils import get_random_string


class Player(BaseModel):
    score: int
    ws: web.WebSocketResponse

    model_config = ConfigDict(arbitrary_types_allowed=True)


class PlayerVerdict(BaseModel):
    round: int
    candidate: str
    verdict: bool


@dataclass
class LotteryState:
    players: dict[str, Player] = field(default_factory=dict)
    verdict: dict[str, PlayerVerdict] | None = None
    round: int = 0
    current_message: str = hashlib.sha256(get_random_string(32).encode()).hexdigest()
    difficulty: int = 10
    players_mutex = threading.Lock()

    def step(self, candidate: str) -> None:
        self.round += 1
        self.current_message = hashlib.sha256(candidate.encode()).hexdigest()
        self.verdict = None

    def add_player(self, ws: web.WebSocketResponse) -> str:
        with self.players_mutex:
            player_id = str(uuid.uuid4())
            self.players[player_id] = Player(ws=ws, score=0)

        return player_id

    def remove_player(self, player_id: str) -> Player | None:
        with self.players_mutex:
            if self.verdict:
                self.verdict.pop(player_id, None)  # removing verdict block if exists
            return self.players.pop(player_id, None)

    def get_current_round_blocks(self):
        assert self.verdict != None, "Attempt to get blocks when verdict is not set"
        return list(
            filter(lambda block: block.round == self.round, self.verdict.values())
        )
