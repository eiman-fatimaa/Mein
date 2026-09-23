"""In-memory cache for outfit analysis results, keyed by image URL.

Resets on server restart -- fine for MVP. Swap for Redis if the server
ever runs multiple instances or needs the cache to survive restarts.
"""

_cache: dict[str, dict] = {}


def get_cached_analysis(image_url: str) -> dict | None:
    return _cache.get(image_url)


def set_cached_analysis(image_url: str, result: dict) -> None:
    _cache[image_url] = result
