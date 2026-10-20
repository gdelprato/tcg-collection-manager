"""Game-agnostic data model. Game-specific details live in the adapters and in rarity.py."""
from datetime import date, datetime, timezone

from sqlmodel import Field, SQLModel, UniqueConstraint


class Game(SQLModel, table=True):
    id: str = Field(primary_key=True)  # "pokemon", "magic"
    name: str


class CardSet(SQLModel, table=True):
    __tablename__ = "card_set"
    __table_args__ = (UniqueConstraint("game_id", "source_id", "language"),)

    id: int | None = Field(default=None, primary_key=True)
    game_id: str = Field(foreign_key="game.id", index=True)
    source: str  # adapter name: "tcgdex", "scryfall"
    source_id: str  # id in the source catalogue ("SV2a", "mkm")
    code: str  # code printed on cards / shown to the user
    name: str
    series: str | None = None
    language: str = "en"
    release_date: date | None = None
    card_count: int | None = None  # cards in the source, secrets included
    official_count: int | None = None  # the "/xxx" printed on cards
    logo_url: str | None = None
    imported_at: datetime | None = None


class Card(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("set_id", "source_id"),)

    id: int | None = Field(default=None, primary_key=True)
    set_id: int = Field(foreign_key="card_set.id", index=True)
    source_id: str
    number: str  # as printed ("064", "123a", "★1")
    sort_key: int = 0  # numeric part of `number`, for ordering
    name: str = Field(index=True)
    rarity_raw: str | None = None  # string as returned by the source
    rarity: str | None = Field(default=None, index=True)  # normalized code, see rarity.py
    image_url: str | None = None


class CollectionItem(SQLModel, table=True):
    """One physical copy group: same card, finish and condition."""

    id: int | None = Field(default=None, primary_key=True)
    card_id: int = Field(foreign_key="card.id", index=True)
    quantity: int = 1
    finish: str = "normal"  # normal | holo | reverse | foil
    condition: str = "NM"  # NM | LP | MP | HP | DMG
    grading: str | None = None  # e.g. "PSA 10"
    notes: str | None = None
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
