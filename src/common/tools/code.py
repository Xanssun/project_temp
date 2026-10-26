import string
from secrets import choice


def generate_code(length: int = 6) -> str:
    alphabet = string.ascii_letters + string.digits
    if length <= 0:
        raise ValueError("length must be positive")
    return "".join(choice(alphabet) for _ in range(length))
