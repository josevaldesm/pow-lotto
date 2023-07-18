import os

def get_random_string(length: int) -> str:
    return os.urandom(int(length / 4)).hex()