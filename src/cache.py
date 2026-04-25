import hashlib
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class QueryCache:
    """
    In-memory semantic cache mimicking a Redis datastore.
    Caches identical queries to save API costs and reduce latency.
    Designed to easily swap to `redis-py` when moving to a distributed production environment.
    """
    def __init__(self):
        self._cache = {}
        logging.info("QueryCache initialized (In-memory mode)")

    def _generate_key(self, query: str) -> str:
        """
        Normalizes the query and generates a SHA-256 hash key.
        This handles minor whitespace or capitalization differences.
        """
        normalized = query.lower().strip()
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    def get(self, query: str):
        key = self._generate_key(query)
        if key in self._cache:
            logging.info("CACHE HIT ⚡: Returning cached result for query (0 API cost)")
            return self._cache[key]
        return None

    def set(self, query: str, result: list):
        key = self._generate_key(query)
        self._cache[key] = result
        logging.info("CACHE SET 💾: Result saved for future identical queries")

# Global singleton instance
semantic_cache = QueryCache()
