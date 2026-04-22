from .repository import init_schema
from .seed import seed_if_empty


def init_app_database() -> None:
    init_schema()
    seed_if_empty()
    print("Database ready (MongoDB)")
