import hashlib

from aiohttp import web
from pydantic import BaseModel, ConfigDict

from proyecto.utils import get_random_string


class Player(BaseModel):
    score: int
    ws: web.WebSocketResponse

    model_config = ConfigDict(arbitrary_types_allowed=True)

class PlayerVerdict(BaseModel):
    round: int
    previous_candidate: str
    current_message: str

class LotteryState(BaseModel):
    players: dict[str, Player] = {}
    verdict: dict[str, list[PlayerVerdict]] = {}
    round: int = 0
    current_message: str = hashlib.sha256(get_random_string(32).encode()).hexdigest()
    difficulty: int = 10
