"""Seed only essential MongoDB system rows."""

from .repository import DEFAULT_ADMIN_SETTINGS, hash_password
from .database import get_collection


def seed_if_empty() -> None:
    admin_coll = get_collection("admin_users")
    settings_coll = get_collection("app_settings")

    if admin_coll.count_documents({}) == 0:
        admin_coll.insert_one(
            {
                "id": "admin-1",
                "name": "Admin User",
                "email": "admin@lawmate.com",
                "password_hash": hash_password("admin123"),
            }
        )

    if settings_coll.find_one({"key": "admin_settings"}) is None:
        settings_coll.insert_one({"key": "admin_settings", "value": dict(DEFAULT_ADMIN_SETTINGS)})
