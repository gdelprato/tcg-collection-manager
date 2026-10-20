"""Rarity normalization per game.

Each source returns its own rarity strings. We keep the raw value on the card and map it to a
short code plus a rank (higher = rarer) so the UI can filter and sort across sets.
Unknown strings are kept as-is with code None; add them here when they show up
(`python -m app.cli rarities` lists the raw values found in the database).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Rarity:
    code: str
    label: str
    rank: int


POKEMON = {
    "common": Rarity("C", "Common", 1),
    "uncommon": Rarity("U", "Uncommon", 2),
    "rare": Rarity("R", "Rare", 3),
    "holo rare": Rarity("R", "Rare", 3),
    "double rare": Rarity("RR", "Double Rare", 4),
    "ace spec rare": Rarity("ACE", "ACE SPEC", 5),
    "illustration rare": Rarity("AR", "Art Rare", 6),
    "art rare": Rarity("AR", "Art Rare", 6),
    "shiny rare": Rarity("S", "Shiny", 6),
    "ultra rare": Rarity("SR", "Super Rare", 7),
    "super rare": Rarity("SR", "Super Rare", 7),
    "shiny ultra rare": Rarity("SSR", "Shiny Super Rare", 7),
    "special illustration rare": Rarity("SAR", "Special Art Rare", 8),
    "special art rare": Rarity("SAR", "Special Art Rare", 8),
    "hyper rare": Rarity("UR", "Ultra Rare (gold)", 9),
    "mega ultra rare": Rarity("MUR", "Mega Ultra Rare", 10),
}

MAGIC = {
    "common": Rarity("C", "Common", 1),
    "uncommon": Rarity("U", "Uncommon", 2),
    "rare": Rarity("R", "Rare", 3),
    "mythic": Rarity("M", "Mythic", 4),
    "special": Rarity("S", "Special", 5),
    "bonus": Rarity("B", "Bonus", 5),
}

TABLES = {"pokemon": POKEMON, "magic": MAGIC}


def normalize(game: str, raw: str | None) -> Rarity | None:
    if not raw:
        return None
    return TABLES.get(game, {}).get(raw.strip().lower())


def rank(game: str, code: str | None) -> int:
    for r in TABLES.get(game, {}).values():
        if r.code == code:
            return r.rank
    return 0
