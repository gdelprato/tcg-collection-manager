"""Contract every catalogue source implements. Parsing is kept in pure functions so it can be
tested against saved JSON fixtures without network access."""

import json
import re
import time
from dataclasses import dataclass
from datetime import date
from hashlib import sha1
from typing import Protocol

import httpx

from ..config import CACHE_DIR, USER_AGENT


@dataclass
class SetData:
    source_id: str
    code: str
    name: str
    series: str | None = None
    release_date: date | None = None
    card_count: int | None = None
    official_count: int | None = None
    logo_url: str | None = None


@dataclass
class CardData:
    source_id: str
    number: str
    name: str
    rarity_raw: str | None = None
    image_url: str | None = None


class SourceAdapter(Protocol):
    game: str
    source: str

    def __init__(self, language: str = "en") -> None: ...
    def list_sets(self) -> list[SetData]: ...
    def fetch_cards(self, set_source_id: str) -> list[CardData]: ...


def sort_key(number: str) -> int:
    m = re.search(r"\d+", number)
    return int(m.group()) if m else 0


def parse_date(value: str | None) -> date | None:
    try:
        return date.fromisoformat(value[:10]) if value else None
    except ValueError:
        return None


class CachedClient:
    """Small HTTP client: polite delay between requests and an on-disk JSON cache.
    Catalogues change rarely, so a cache avoids hammering free community APIs."""

    def __init__(self, min_interval: float, ttl_hours: float = 24.0):
        self.min_interval = min_interval
        self.ttl = ttl_hours * 3600
        self._last = 0.0
        self.http = httpx.Client(
            timeout=30,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            follow_redirects=True,
        )

    def get_json(self, url: str, use_cache: bool = True):
        path = CACHE_DIR / (sha1(url.encode()).hexdigest() + ".json")
        if use_cache and path.exists() and time.time() - path.stat().st_mtime < self.ttl:
            return json.loads(path.read_text())
        wait = self.min_interval - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        resp = self.http.get(url)
        self._last = time.monotonic()
        resp.raise_for_status()
        data = resp.json()
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
        return data
