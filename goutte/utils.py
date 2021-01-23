import uuid
from datetime import date


def get_id() -> str:
    return uuid.uuid4().hex[:5]


def get_date(fmt: str = "%Y%m%d") -> str:
    return date.today().strftime(fmt)
