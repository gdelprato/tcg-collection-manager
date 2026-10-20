from datetime import date

from pydantic import BaseModel, Field


class SetOut(BaseModel):
    id: int
    game_id: str
    code: str
    name: str
    series: str | None
    language: str
    release_date: date | None
    card_count: int | None
    official_count: int | None
    logo_url: str | None
    imported: int = 0  # cards present in the local catalogue
    owned: int = 0  # distinct cards owned


class CardOut(BaseModel):
    id: int
    number: str
    name: str
    rarity: str | None
    rarity_raw: str | None
    image_url: str | None
    owned_quantity: int = 0


class SetDetail(SetOut):
    cards: list[CardOut]


class ItemIn(BaseModel):
    card_id: int
    quantity: int = Field(1, ge=1)
    finish: str = "normal"
    condition: str = "NM"
    grading: str | None = None
    notes: str | None = None


class ItemPatch(BaseModel):
    quantity: int | None = Field(None, ge=1)
    finish: str | None = None
    condition: str | None = None
    grading: str | None = None
    notes: str | None = None


class QuantityIn(BaseModel):
    quantity: int = Field(..., ge=0)


class ImportIn(BaseModel):
    game: str
    set_id: str
    language: str = "en"
