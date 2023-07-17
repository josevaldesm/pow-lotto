import asyncio
import hashlib
import random
import string

from pydantic import BaseModel

from client.messages.server import LotteryStateMessageWithId, CandidateMessage, LotteryStateMessage
from client.controller.base import Controller

class LotteryState(BaseModel):
    player_id: str
    round: int
    k: int
    current_message: str


class PlayerController(Controller):
    def __init__(self, event: asyncio.Event):
        super().__init__(event)
        self.__state: LotteryState | None = None
        self.__compute_task: asyncio.Task | None = None
        self.__computing = True

    @property
    def state(self) -> LotteryState:
        if self.__state is None:
            raise ValueError("Cannot get state because is not setted yet")
        
        return self.__state
    
    @state.setter
    def state(self, new: LotteryState) -> None:
        self.__state = new

    async def __compute(self):
        print(f"Player ID {self.state.player_id} is computing...")
        vi = self.state.current_message
        pid = self.state.player_id
        k = self.state.k

        attempt = 1
        alphabet = (
            string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase
        )
        length = random.randint(6, 26)
        ri = "".join(random.choices(alphabet, k=length))

        candidate = hashlib.sha3_256(f"{vi}{pid}{ri}".encode()).hexdigest()
        lsb = bin(int(candidate, 16))[-k:]
        found = lsb == "".join(["0" for _ in range(k)])
        while not found and self.__computing:
            attempt += 1
            length = random.randint(6, 26)
            ri = "".join(random.choices(alphabet, k=length))
            candidate = hashlib.sha3_256(f"{vi}{pid}{ri}".encode()).hexdigest()
            lsb = bin(int(candidate, 16))[-k:]
            found = lsb == "".join(["0" for _ in range(k)])
            await asyncio.sleep(0.01)

        if not found:
            print("Compute interrupted")
            return None
        
        message = {"channel": "CANDIDATE", "data": {"r": ri}}
        print(f"Player ID {pid}: {message}")
        await self.ws.send_json(message)

    def start_computing_task(self):
        self.__computing = True
        self.__compute_task = asyncio.create_task(self.__compute())

    def stop_compute_task(self):
        self.__computing = False
        if self.__compute_task:
            self.__compute_task.cancel()

    async def on_connect(
        self, data: LotteryStateMessageWithId
    ):
        self.state = LotteryState(
            player_id=data.player_id,
            round=data.round,
            k=data.k,
            current_message=data.current_message,
        )
        self.start_computing_task()

    async def on_found_candidate(self, data: CandidateMessage):
        self.stop_compute_task()
        vi = self.state.current_message
        pid = data.player_id
        ri = data.r
        k = self.state.k

        hexdigest = hashlib.sha3_256(f"{vi}{pid}{ri}".encode()).hexdigest()
        lsb = bin(int(hexdigest, 16))[-k:]
        verdict = lsb == "".join(["0" for _ in range(k)])
        await self.ws.send_json(
            {
                "channel": "LOTTERY_STATE",
                "data": {
                    "round": self.state.round,
                    "candidate": f"{pid}{ri}",
                    "verdict": verdict,
                },
            }
        )

    async def on_lottery_message(
        self, data: LotteryStateMessage
    ):
        self.stop_compute_task()
        self.state = LotteryState(
            player_id=self.state.player_id,
            round=data.round,
            k=data.k,
            current_message=data.current_message,
        )
        self.start_computing_task()

    async def on_disconnect(self):
        self.__state = None
