"""
fetch_data.py
Fetches top ~500 popular movies from TMDB, looks up each on DoesTheDogDie,
and outputs data/movies.json for the static site to consume.

Required environment variables:
  TMDB_API_KEY   — from themoviedb.org
  DTDD_API_KEY   — from doesthedogdie.com/profile
"""

import os
import json
import time
import logging
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

TMDB_KEY = os.environ["TMDB_API_KEY"]
DTDD_KEY = os.environ["DTDD_API_KEY"]

TMDB_BASE = "https://api.themoviedb.org/3"
DTDD_BASE = "https://www.doesthedogdie.com"

# DTDD topic ID for "dogs dying" — confirmed from their API docs
DOGS_DYING_TOPIC_ID = 1  # topic 1 = "Does the dog die?"

# Minimum DTDD votes to include a film (filters out obscure/unrated titles)
MIN_DTDD_VOTES = 20

# Minimum box office to include (filters out unreported/VOD-only releases)
MIN_BOX_OFFICE = 1_000_000

PAGES_TO_FETCH = 25  # 25 pages × 20 results = 500 movies


def tmdb_get(path: str, params: dict = None) -> dict:
    params = params or {}
    params["api_key"] = TMDB_KEY
    r = requests.get(f"{TMDB_BASE}{path}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def dtdd_get(path: str) -> dict:
    headers = {"X-API-KEY": DTDD_KEY}
    r = requests.get(f"{DTDD_BASE}{path}", headers=headers, timeout=10)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def fetch_popular_movie_ids() -> list[int]:
    """Return TMDB IDs for the top ~500 popular movies."""
    ids = []
    for page in range(1, PAGES_TO_FETCH + 1):
        log.info(f"Fetching TMDB popular movies page {page}/{PAGES_TO_FETCH}")
        data = tmdb_get("/movie/popular", {"language": "en-US", "page": page})
        ids.extend(m["id"] for m in data.get("results", []))
        time.sleep(0.25)  # stay well within TMDB rate limits
    log.info(f"Found {len(ids)} TMDB movie IDs")
    return ids


def fetch_tmdb_details(tmdb_id: int) -> dict | None:
    """Return box office + metadata for a single movie."""
    try:
        d = tmdb_get(f"/movie/{tmdb_id}", {"language": "en-US"})
        revenue = d.get("revenue", 0)
        if not revenue or revenue < MIN_BOX_OFFICE:
            return None
        return {
            "tmdb_id": tmdb_id,
            "title": d.get("title", ""),
            "year": (d.get("release_date", "") or "")[:4],
            "revenue": revenue,
            "budget": d.get("budget", 0),
            "genres": [g["name"] for g in d.get("genres", [])],
            "poster_path": d.get("poster_path", ""),
            "overview": d.get("overview", ""),
        }
    except requests.HTTPError:
        return None


def fetch_dtdd_rating(tmdb_id: int) -> dict | None:
    """
    Return dog-death confidence score for a TMDB movie ID.
    DTDD's API accepts TMDB IDs directly via /api/media/topic/does-the-dog-die/{tmdb_id}
    Returns dict with keys: yesVotes, noVotes, ratio (0.0–1.0), totalVotes
    """
    try:
        # First get the media entry
        media = dtdd_get(f"/api/media/{tmdb_id}")
        if not media:
            return None

        # Find the "dogs dying" topic in the item's topics list
        topics = media.get("topicItemStats", [])
        for t in topics:
            if t.get("topic", {}).get("id") == DOGS_DYING_TOPIC_ID:
                yes = t.get("yesSum", 0)
                no = t.get("noSum", 0)
                total = yes + no
                if total < MIN_DTDD_VOTES:
                    return None
                return {
                    "yes_votes": yes,
                    "no_votes": no,
                    "total_votes": total,
                    "dog_dies_pct": round(yes / total * 100, 1) if total else None,
                }
    except (requests.HTTPError, KeyError, TypeError):
        pass
    return None


def main():
    out_path = Path(__file__).parent.parent / "data" / "movies.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tmdb_ids = fetch_popular_movie_ids()

    results = []
    dtdd_calls = 0

    for i, tmdb_id in enumerate(tmdb_ids):
        if i % 50 == 0:
            log.info(f"Processing movie {i}/{len(tmdb_ids)} — {len(results)} kept so far")

        movie = fetch_tmdb_details(tmdb_id)
        if not movie:
            time.sleep(0.1)
            continue

        time.sleep(0.1)  # TMDB rate limit buffer

        # DTDD free tier: 30 req/min = 1 per 2 sec to be safe
        dtdd = fetch_dtdd_rating(tmdb_id)
        dtdd_calls += 1
        time.sleep(2.1)

        if not dtdd:
            continue

        results.append({**movie, **dtdd})
        log.info(f"  ✓ {movie['title']} ({movie['year']}) — dog dies: {dtdd['dog_dies_pct']}% | box office: ${movie['revenue']:,}")

    log.info(f"Done. {len(results)} movies with both box office and DTDD data.")
    log.info(f"DTDD API calls used: {dtdd_calls}")

    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    log.info(f"Written to {out_path}")


if __name__ == "__main__":
    main()
