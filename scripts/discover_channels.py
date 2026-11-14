import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from yt_pipeline import config  # noqa: E402
from yt_pipeline.quota import QuotaGuard  # noqa: E402
from yt_pipeline.youtube_client import YouTubeClient  # noqa: E402

CHANNELS_FILE = ROOT / "data" / "channels.csv"


def existing_ids() -> set[str]:
    if not CHANNELS_FILE.exists():
        return set()
    with CHANNELS_FILE.open(newline="", encoding="utf-8") as f:
        return {r["channel_id"] for r in csv.DictReader(f) if r.get("channel_id")}


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python scripts/discover_channels.py "search phrase"')
        return 1
    query = sys.argv[1]
    client = YouTubeClient(config.youtube_api_key(), QuotaGuard(config.quota_limit()))
    results = client.search_channels(query)

    seen = existing_ids()
    new_rows = []
    for item in results:
        channel_id = item["snippet"]["channelId"]
        if channel_id not in seen:
            new_rows.append({"channel_id": channel_id, "channel_name": item["snippet"]["title"]})
            seen.add(channel_id)

    write_header = not CHANNELS_FILE.exists() or CHANNELS_FILE.stat().st_size == 0
    with CHANNELS_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["channel_id", "channel_name"])
        if write_header:
            writer.writeheader()
        writer.writerows(new_rows)

    print(f"Added {len(new_rows)} channels to {CHANNELS_FILE}. Quota used: 100 units.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())