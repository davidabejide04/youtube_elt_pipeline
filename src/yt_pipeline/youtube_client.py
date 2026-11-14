import logging

from googleapiclient.discovery import build

from .quota import QuotaGuard

log = logging.getLogger(__name__)
BATCH_SIZE = 50  # the API accepts up to 50 ids per request


def chunks(items: list, size: int = BATCH_SIZE):
    for i in range(0, len(items), size):
        yield items[i : i + size]


class YouTubeClient:
    def __init__(self, api_key: str, guard: QuotaGuard):
        self.guard = guard
        self._yt = build("youtube", "v3", developerKey=api_key, cache_discovery=False)

    def get_channels(self, channel_ids: list[str]) -> list[dict]:
        items: list[dict] = []
        for batch in chunks(channel_ids):
            self.guard.charge("channels.list")
            resp = (
                self._yt.channels()
                .list(part="snippet,statistics,contentDetails", id=",".join(batch))
                .execute(num_retries=3)
            )
            items.extend(resp.get("items", []))
        return items

    def get_upload_video_ids(self, uploads_playlist_id: str, max_videos: int = 50) -> list[str]:
        self.guard.charge("playlistItems.list")
        resp = (
            self._yt.playlistItems()
            .list(
                part="contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=min(max_videos, 50),
            )
            .execute(num_retries=3)
        )
        return [i["contentDetails"]["videoId"] for i in resp.get("items", [])]

    def get_videos(self, video_ids: list[str]) -> list[dict]:
        items: list[dict] = []
        for batch in chunks(video_ids):
            self.guard.charge("videos.list")
            resp = (
                self._yt.videos()
                .list(part="snippet,statistics,contentDetails", id=",".join(batch))
                .execute(num_retries=3)
            )
            items.extend(resp.get("items", []))
        return items

    def search_channels(self, query: str, max_results: int = 50) -> list[dict]:
        """Costs 100 units."""
        self.guard.charge("search.list")
        resp = (
            self._yt.search()
            .list(part="snippet", q=query, type="channel", maxResults=min(max_results, 50))
            .execute(num_retries=3)
        )
        return resp.get("items", [])