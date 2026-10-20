"""Pokémon catalogue from TCGdex (https://tcgdex.dev), REST v2.

URL pattern: https://api.tcgdex.net/v2/{lang}/sets, /sets/{id}, /cards/{id}
The set endpoint returns card briefs without rarity, so rarity needs one request per card;
results are cached on disk. TODO: try the GraphQL endpoint (api.tcgdex.net/v2/graphql) to
fetch a whole set with rarities in one call.
"""

from .base import CachedClient, CardData, SetData, parse_date

BASE = "https://api.tcgdex.net/v2"


def image_url(base: str | None, quality: str = "high", ext: str = "webp") -> str | None:
    return f"{base}/{quality}.{ext}" if base else None


def parse_set_brief(item: dict) -> SetData:
    count = item.get("cardCount") or {}
    return SetData(
        source_id=item["id"],
        code=item["id"],
        name=item.get("name", item["id"]),
        card_count=count.get("total"),
        official_count=count.get("official"),
        logo_url=item.get("logo"),
    )


def parse_set(detail: dict) -> SetData:
    s = parse_set_brief(detail)
    s.series = (detail.get("serie") or {}).get("name")
    s.release_date = parse_date(detail.get("releaseDate"))
    return s


def parse_card(detail: dict) -> CardData:
    return CardData(
        source_id=detail["id"],
        number=str(detail.get("localId", "")),
        name=detail.get("name", ""),
        rarity_raw=detail.get("rarity"),
        image_url=image_url(detail.get("image")),
    )


class TCGdexAdapter:
    game = "pokemon"
    source = "tcgdex"

    def __init__(self, language: str = "en"):
        self.language = language  # "en", "ja", "it", ...
        self.client = CachedClient(min_interval=0.05)

    def _url(self, path: str) -> str:
        return f"{BASE}/{self.language}/{path}"

    def list_sets(self) -> list[SetData]:
        return [parse_set_brief(i) for i in self.client.get_json(self._url("sets"))]

    def get_set(self, set_id: str) -> SetData:
        return parse_set(self.client.get_json(self._url(f"sets/{set_id}")))

    def fetch_cards(self, set_source_id: str) -> list[CardData]:
        detail = self.client.get_json(self._url(f"sets/{set_source_id}"))
        cards = []
        for brief in detail.get("cards", []):
            card = self.client.get_json(self._url(f"cards/{brief['id']}"))
            cards.append(parse_card(card))
        return cards
