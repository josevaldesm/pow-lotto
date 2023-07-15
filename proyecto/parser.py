import argparse
from dataclasses import dataclass


@dataclass
class ServerParameters:
    host: str
    port: str


def get_args() -> ServerParameters:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=str, default="8080")
    return ServerParameters(**vars(parser.parse_args()))
