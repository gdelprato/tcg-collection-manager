from .base import CardData, SetData, SourceAdapter
from .scryfall import ScryfallAdapter
from .tcgdex import TCGdexAdapter

ADAPTERS: dict[str, type[SourceAdapter]] = {"pokemon": TCGdexAdapter, "magic": ScryfallAdapter}

__all__ = ["ADAPTERS", "CardData", "SetData", "SourceAdapter"]
