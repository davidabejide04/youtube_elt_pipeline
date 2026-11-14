"""Tracks estimated YouTube API quota so the pipeline never exceeds the free limit."""

COSTS = {
    "channels.list": 1,
    "playlistItems.list": 1,
    "videos.list": 1,
    "search.list": 100,
}


class QuotaExceeded(Exception):
    """Raised when a call would push estimated usage past the configured limit."""


class QuotaGuard:
    def __init__(self, limit: int = 8000):
        self.limit = limit
        self.used = 0

    def charge(self, endpoint: str) -> None:
        cost = COSTS[endpoint]
        if self.used + cost > self.limit:
            raise QuotaExceeded(
                f"{endpoint} would exceed the limit of {self.limit} units (used {self.used})"
            )
        self.used += cost
