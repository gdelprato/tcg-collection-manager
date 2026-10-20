from datetime import datetime, timezone

from sqlmodel import Session, select

from . import rarity
from .adapters.base import CardData, SetData, sort_key
from .models import Card, CardSet


def upsert_set(s: Session, game: str, source: str, language: str, data: SetData) -> CardSet:
    row = s.exec(
        select(CardSet).where(
            CardSet.game_id == game, CardSet.source_id == data.source_id, CardSet.language == language
        )
    ).first()
    if row is None:
        row = CardSet(game_id=game, source=source, source_id=data.source_id, language=language, code=data.code, name=data.name)
    for field in ("code", "name", "series", "release_date", "card_count", "official_count", "logo_url"):
        value = getattr(data, field)
        if value is not None:
            setattr(row, field, value)
    s.add(row)
    s.flush()
    return row


def upsert_cards(s: Session, game: str, card_set: CardSet, cards: list[CardData]) -> int:
    existing = {c.source_id: c for c in s.exec(select(Card).where(Card.set_id == card_set.id))}
    for data in cards:
        row = existing.get(data.source_id) or Card(set_id=card_set.id, source_id=data.source_id, number=data.number, name=data.name)
        norm = rarity.normalize(game, data.rarity_raw)
        row.number, row.name, row.image_url = data.number, data.name, data.image_url
        row.sort_key = sort_key(data.number)
        row.rarity_raw = data.rarity_raw
        row.rarity = norm.code if norm else None
        s.add(row)
    card_set.card_count = card_set.card_count or len(cards)
    card_set.imported_at = datetime.now(timezone.utc)
    s.add(card_set)
    return len(cards)


def import_set(s: Session, adapter, set_data: SetData) -> CardSet:
    """Import one set (metadata + cards) using an adapter instance."""
    row = upsert_set(s, adapter.game, adapter.source, adapter.language, set_data)
    upsert_cards(s, adapter.game, row, adapter.fetch_cards(set_data.source_id))
    s.commit()
    s.refresh(row)
    return row
