import argparse
from dataclasses import dataclass


@dataclass
class ServerParameters:
    host: str
    port: str
    difficulty: int
    max_rounds: int


def get_args() -> ServerParameters:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=str, default="8080")
    parser.add_argument("--difficulty", type=int, default=1)
    parser.add_argument("--max-rounds", type=int, default=-1)
    return ServerParameters(**vars(parser.parse_args()))
