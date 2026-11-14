import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing environment variable {name}. Copy .env.example to .env and fill it in."
        )
    return value


def resolve_path(value: str) -> str:
    """Make a path absolute and relative to the project root."""
    path = Path(value)
    return str(path if path.is_absolute() else (ROOT / path).resolve())


def youtube_api_key() -> str:
    return _require("YOUTUBE_API_KEY")


def quota_limit() -> int:
    return int(os.getenv("QUOTA_LIMIT", "8000"))


def snowflake_params() -> dict:
    params = {
        "account": _require("SNOWFLAKE_ACCOUNT"),
        "user": _require("SNOWFLAKE_USER"),
        "private_key_file": resolve_path(_require("SNOWFLAKE_PRIVATE_KEY_PATH")),
        "warehouse": _require("SNOWFLAKE_WAREHOUSE"),
        "database": _require("SNOWFLAKE_DATABASE"),
        "schema": "RAW",
        "role": os.getenv("SNOWFLAKE_ROLE", "LOADER"),
    }
    passphrase = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE")
    if passphrase:
        params["private_key_file_pwd"] = passphrase
    return params