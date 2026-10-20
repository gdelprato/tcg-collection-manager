"""Magic catalogue from Scryfall (https://scryfall.com/docs/api).

Scryfall asks for 50-100 ms between requests and an identifying User-Agent + Accept header.
Cards of a set: /cards/search?q=e:{code}&unique=prints&order=set, paginated via next_page.
For a full-catalogue import, use the daily bulk data files instead of searching set by set.
"""

from urllib.parse import quote

from .base import CachedClient, CardData, SetData, parse_date

BASE = "https://api.scryfall.com"
# Set types that are real card sets for a collector; tokens, memorabilia etc. are skipped.
COLLECTIBLE_TYPES = {
    "core", "expansion", "masters", "draft_innovation", "commander",
    "funny", "starter", "box", "masterpiece", "promo", "duel_deck", "from_the_vault",
}


def parse_set(item: dict) -> SetData:
    return SetData(
        source_id=item["code"],
        code=item["code"].upper(),
        name=item["name"],
        series=item.get("set_type"),
        release_date=parse_date(item.get("released_at")),
        card_count=item.get("card_count"),
        official_count=item.get("printed_size") or item.get("card_count"),
        logo_url=item.get("icon_svg_uri"),
    )


def card_image(card: dict) -> str | None:
    uris = card.get("image_uris")
    if not uris and card.get("card_faces"):  # double-faced cards
        uris = card["card_faces"][0].get("image_uris")
    return (uris or {}).get("normal")


def parse_card(card: dict) -> CardData:
    return CardData(
        source_id=card["id"],
        number=card.get("collector_number", ""),
        name=card.get("printed_name") or card.get("name", ""),
        rarity_raw=card.get("rarity"),
        image_url=card_image(card),
    )


class ScryfallAdapter:
    game = "magic"
    source = "scryfall"

    def __init__(self, language: str = "en"):
        self.language = language
        self.client = CachedClient(min_interval=0.1)

    def list_sets(self) -> list[SetData]:
        data = self.client.get_json(f"{BASE}/sets")["data"]
        return [parse_set(s) for s in data if s.get("set_type") in COLLECTIBLE_TYPES and not s.get("digital")]

    def get_set(self, code: str) -> SetData:
        return parse_set(self.client.get_json(f"{BASE}/sets/{code}"))

    def fetch_cards(self, set_source_id: str) -> list[CardData]:
        q = f"e:{set_source_id} lang:{self.language}"
        url = f"{BASE}/cards/search?q={quote(q)}&unique=prints&order=set&include_extras=true"
        cards: list[CardData] = []
        while url:
            page = self.client.get_json(url)
            cards += [parse_card(c) for c in page.get("data", [])]
            url = page.get("next_page") if page.get("has_more") else None
        return cards
