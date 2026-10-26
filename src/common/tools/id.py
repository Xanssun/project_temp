import time
from datetime import datetime


def gen_human_id() -> str:
    today = datetime.now().strftime("%Y%m%d")
    now = int(time.time() * 1000)
    return f"{today}-{now % 1000000}"
