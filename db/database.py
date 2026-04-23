import os
from functools import lru_cache

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING", "").strip()
MONGODB_DATABASE_NAME = os.environ.get("MONGODB_DATABASE_NAME", "FYP_VirtualLawyer").strip() or "FYP_VirtualLawyer"


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    if not MONGODB_CONNECTION_STRING:
        raise RuntimeError("MONGODB_CONNECTION_STRING is not set. Please configure it in .env")
    return MongoClient(
        MONGODB_CONNECTION_STRING,
        retryWrites=True,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=15000,
    )


@lru_cache(maxsize=1)
def get_database():
    return get_client()[MONGODB_DATABASE_NAME]


def get_collection(name: str):
    return get_database()[name]
