# core/stream_cache_service.py
from core.database import get_db



class StreamCacheService:
    """
    Simple service to cache movie streams in the database.
    This allows us to store results from plugin scans and quickly retrieve them
    without re-scanning plugins every time.
    """

    def __init__(self):
        self.db = get_db()

    def save_movies(self, plugin_name: str, movies: list[dict]):
        data = [
            dict(
                plugin_name=plugin_name,
                title=m.get("title"),
                url=m.get("url")
            )
            for m in movies
        ]

        self.db.stream_cache.bulk_insert(data)
        self.db.commit()

    def get_all(self):
        rows = self.db(self.db.stream_cache).select()
        return rows.as_list()
