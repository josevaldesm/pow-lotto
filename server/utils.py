import random
import string


def get_random_string(length: int) -> str:
    alphabet = string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase
    return "".join([random.choice(alphabet) for _ in range(length)])
