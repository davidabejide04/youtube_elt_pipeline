import argparse
import csv
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from yt_pipeline import config  # noqa: E402
from yt_pipeline.extract import (  # noqa: E402
    INT_COLUMNS_CHANNELS,
    INT_COLUMNS_VIDEOS,
    extract_channels,
    extract_videos,
    now_utc,
    to_dataframe,
)
from yt_pipeline.logging_setup import configure_logging  # noqa: E402
from yt_pipeline.quota import QuotaExceeded, QuotaGuard  # noqa: E402
from yt_pipeline.youtube_client import YouTubeClient  # noqa: E402

log = logging.getLogger("pipeline")
CHANNELS_FILE = ROOT / "data" / "channels.csv"


def read_channel_ids(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as f:
        ids = [row["channel_id"].strip() for row in csv.DictReader(f) if row.get("channel_id")]
    if not ids:
        raise SystemExit(
            f"{path} has no channels. Run `python scripts/discover_channels.py \"data analysis\"` first."
        )
    return list(dict.fromkeys(ids))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract-only", action="store_true", help="skip Snowflake, write CSVs")
    parser.add_argument("--max-videos", type=int, default=50, help="latest videos tracked per channel")
    args = parser.parse_args()

    configure_logging()
    channel_ids = read_channel_ids(CHANNELS_FILE)
    guard = QuotaGuard(config.quota_limit())
    client = YouTubeClient(config.youtube_api_key(), guard)

    loaded_at = now_utc()
    snapshot_date = loaded_at.date()

    try:
        channels = extract_channels(client, channel_ids, snapshot_date, loaded_at)
        videos = extract_videos(client, channels, snapshot_date, loaded_at, args.max_videos)
    except QuotaExceeded as err:
        log.error("Stopped to protect the free quota: %s. Nothing was loaded.", err)
        return 1

    log.info("Extracted %d channels and %d videos. Quota used: %d/%d",
             len(channels), len(videos), guard.used, guard.limit)

    channels_df = to_dataframe(channels, INT_COLUMNS_CHANNELS)
    videos_df = to_dataframe(videos, INT_COLUMNS_VIDEOS)

    if args.extract_only:
        out = ROOT / "data" / "output"
        out.mkdir(parents=True, exist_ok=True)
        channels_df.to_csv(out / "channels.csv", index=False)
        videos_df.to_csv(out / "videos.csv", index=False)
        log.info("Saved CSVs to %s", out)
        return 0

    from yt_pipeline import load  # imported here so --extract-only needs no Snowflake

    params = config.snowflake_params()
    conn = load.connect(params)
    try:
        load.ensure_tables(conn)
        load.load_dataframe(conn, channels_df, "RAW_CHANNELS", params["database"])
        load.load_dataframe(conn, videos_df, "RAW_VIDEOS", params["database"])
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())