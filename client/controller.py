import asyncio
import hashlib
import random
import string

from aiohttp import ClientWebSocketResponse
from pydantic import BaseModel


from client.messages.server import LotteryStateMessageWithId, LotteryStateMessage


class LotteryState(BaseModel):
    player_id: str
    round: int
    k: int
    current_message: str


class PlayerController:
    def __init__(self, event: asyncio.Event):
        self.__state: LotteryState | None = None
        self.__compute_task: asyncio.Task | None = None
        self.event = event

    @property
    def state(self) -> LotteryState | None:
        return self.__state

    async def __compute(
        self, player_id: str, v: str, k: int, ws: ClientWebSocketResponse
    ) -> str | None:
        attempt = 1
        alphabet = (
            string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase
        )
        length = random.randint(6, 26)
        r = "".join(random.choices(alphabet, k=length))
        candidate = hashlib.sha3_256(f"{v}{player_id}{r}".encode()).hexdigest()
        found = candidate[-k:] == "".join(["0" for _ in range(k)])
        print(f"Attempt {attempt}: {candidate}")
        while not found:
            attempt += 1
            length = random.randint(6, 26)
            r = "".join(random.choices(alphabet, k=length))
            candidate = hashlib.sha3_256(f"{v}{player_id}{r}".encode()).hexdigest()
            print(f"Attempt {attempt}: {candidate}")
            found = candidate[-k:] == "".join(["0" for _ in range(k)])

        if found:
            print(f"Found!\n \tv={v}\n\tpid={player_id}\n\tr={r}")
            await ws.send_json({"channel": "CANDIDATE", "data": {"r": r}})

        return None

    async def on_connect(
        self, state: LotteryStateMessageWithId, ws: ClientWebSocketResponse
    ):
        self.__state = LotteryState(
            player_id=state.player_id,
            round=state.round,
            k=state.k,
            current_message=state.current_message,
        )
        self.__compute_task = asyncio.create_task(
            self.__compute(
                player_id=state.player_id, v=state.current_message, k=state.k, ws=ws
            )
        )

    async def on_lottery_message(
        self, state: LotteryStateMessage, ws: ClientWebSocketResponse
    ):
        if self.__state is None:
            raise ValueError("Can't listen to lottery channel if state is not set")

        self.__state = LotteryState(
            player_id=self.__state.player_id,
            round=state.round,
            k=state.k,
            current_message=state.current_message
        )

        self.__compute_task = asyncio.create_task(
            self.__compute(
                player_id=self.__state.player_id, v=state.current_message, k=state.k, ws=ws
            )
        )

    async def stop_compute_task(self):
        if self.__compute_task:
            self.__compute_task.cancel()

    async def on_disconnect(self):
        self.__state = None
