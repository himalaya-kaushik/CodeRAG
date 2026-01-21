# cache.py

import os
import json
import hashlib

def get_cache_path(project_id: str) -> str:
    """Get cache file path for the current project."""
    cache_dir = os.path.join(os.path.expanduser("~"), ".codebuddy_cache")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, f"cache_{project_id}.json")

def load_cache(cache_path: str) -> dict:
    """Load cached responses from disk."""
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache_path: str, cache: dict):
    """Save updated cache to disk."""
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

def get_query_key(query: str) -> str:
    """Generate a unique hash key for each query string."""
    return hashlib.md5(query.strip().lower().encode()).hexdigest()
