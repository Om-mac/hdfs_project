import datetime


def log(message, level="info"):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tag = level.upper()
    print(f"[{now}] [{tag}] {message}")