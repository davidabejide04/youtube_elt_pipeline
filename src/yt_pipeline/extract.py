import json
import logging
from datetime import date, datetime, timezone

import pandas as pd
from googleapiclient.errors import HttpError

log = logging.getLogger(__name__)


def _to_int(value):
    return None if value is None else int(value)


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def flatten_channel(item: dict, snapshot_date: date, loaded_at: datetime) -> dict:
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    uploads = item.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
    return {
        "channel_id": item["id"],
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "country": snippet.get("country"),
        "published_at": snippet.get("publishedAt"),
        "subscriber_count": _to_int(stats.get("subscriberCount")),
        "hidden_subscriber_count": bool(stats.get("hiddenSubscriberCount", False)),
        "view_count": _to_int(stats.get("viewCount")),
        "video_count": _to_int(stats.get("videoCount")),
        "uploads_playlist_id": uploads,
        "snapshot_date": snapshot_date,
        "loaded_at": loaded_at,
    }


def flatten_video(item: dict, snapshot_date: date, loaded_at: datetime) -> dict:
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    tags = snippet.get("tags")
    return {
        "video_id": item["id"],
        "channel_id": snippet.get("channelId"),
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "published_at": snippet.get("publishedAt"),
        "duration": item.get("contentDetails", {}).get("duration"),
        "category_id": snippet.get("categoryId"),
        "tags": json.dumps(tags) if tags else None,
        "view_count": _to_int(stats.get("viewCount")),
        "like_count": _to_int(stats.get("likeCount")),
        "comment_count": _to_int(stats.get("commentCount")),
        "snapshot_date": snapshot_date,
        "loaded_at": loaded_at,
    }


def extract_channels(client, channel_ids: list[str], snapshot_date: date, loaded_at: datetime) -> list[dict]:
    items = client.get_channels(channel_ids)
    found = {i["id"] for i in items}
    missing = set(channel_ids) - found
    if missing:
        log.warning("Channels not returned by the API: %s", sorted(missing))
    return [flatten_channel(i, snapshot_date, loaded_at) for i in items]


def extract_videos(
    client,
    channel_rows: list[dict],
    snapshot_date: date,
    loaded_at: datetime,
    max_videos_per_channel: int = 50,
) -> list[dict]:
    video_ids: list[str] = []
    for row in channel_rows:
        playlist_id = row.get("uploads_playlist_id")
        if not playlist_id:
            continue
        try:
            video_ids.extend(client.get_upload_video_ids(playlist_id, max_videos_per_channel))
        except HttpError as err:
            log.warning("Skipping channel %s: %s", row["channel_id"], err)
    video_ids = list(dict.fromkeys(video_ids))  # de-duplicate, keep order
    items = client.get_videos(video_ids)
    return [flatten_video(i, snapshot_date, loaded_at) for i in items]


INT_COLUMNS_CHANNELS = ["subscriber_count", "view_count", "video_count"]
INT_COLUMNS_VIDEOS = ["view_count", "like_count", "comment_count"]


def to_dataframe(rows: list[dict], int_columns: list[str]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    for col in int_columns:
        if col in df.columns:
            df[col] = df[col].astype("Int64") 
    return df