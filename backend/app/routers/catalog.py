from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select

from ..db import get_session
from ..models import Card, CardSet, CollectionItem, Game
from ..rarity import rank
from ..schemas import CardOut, SetDetail, SetOut

router = APIRouter(prefix="/api", tags=["catalog"])


def owned_by_card(s: Session, set_id: int | None = None) -> dict[int, int]:
    q = select(CollectionItem.card_id, func.sum(CollectionItem.quantity)).group_by(CollectionItem.card_id)
    if set_id is not None:
        q = q.join(Card, Card.id == CollectionItem.card_id).where(Card.set_id == set_id)
    return {cid: int(qty) for cid, qty in s.exec(q)}


def set_out(row: CardSet, imported: int, owned: int) -> SetOut:
    return SetOut(**row.model_dump(include=set(SetOut.model_fields) - {"imported", "owned"}), imported=imported, owned=owned)


@router.get("/games")
def list_games(s: Session = Depends(get_session)) -> list[Game]:
    return list(s.exec(select(Game)))


@router.get("/sets", response_model=list[SetOut])
def list_sets(game: str | None = None, language: str | None = None, q: str | None = None, s: Session = Depends(get_session)):
    stmt = select(CardSet)
    if game:
        stmt = stmt.where(CardSet.game_id == game)
    if language:
        stmt = stmt.where(CardSet.language == language)
    if q:
        like = f"%{q}%"
        stmt = stmt.where((CardSet.name.ilike(like)) | (CardSet.code.ilike(like)))
    rows = list(s.exec(stmt.order_by(CardSet.release_date.desc(), CardSet.code)))
    counts = dict(s.exec(select(Card.set_id, func.count()).group_by(Card.set_id)).all())
    owned = dict(
        s.exec(
            select(Card.set_id, func.count(func.distinct(Card.id)))
            .join(CollectionItem, CollectionItem.card_id == Card.id)
            .group_by(Card.set_id)
        ).all()
    )
    return [set_out(r, counts.get(r.id, 0), owned.get(r.id, 0)) for r in rows]


@router.get("/sets/{set_id}", response_model=SetDetail)
def get_set(set_id: int, rarity: str | None = None, s: Session = Depends(get_session)):
    row = s.get(CardSet, set_id)
    if not row:
        raise HTTPException(404, "Set non trovato")
    cards = list(s.exec(select(Card).where(Card.set_id == set_id).order_by(Card.sort_key, Card.number)))
    total = len(cards)
    if rarity:
        wanted = {r.strip().upper() for r in rarity.split(",")}
        cards = [c for c in cards if (c.rarity or "") in wanted]
    owned = owned_by_card(s, set_id)
    base = set_out(row, total, sum(1 for c in cards if c.id in owned))
    return SetDetail(
        **base.model_dump(),
        cards=[CardOut(**c.model_dump(include=set(CardOut.model_fields) - {"owned_quantity"}), owned_quantity=owned.get(c.id, 0)) for c in cards],
    )


@router.get("/sets/{set_id}/rarities")
def set_rarities(set_id: int, s: Session = Depends(get_session)) -> list[dict]:
    row = s.get(CardSet, set_id)
    if not row:
        raise HTTPException(404, "Set non trovato")
    found = s.exec(select(Card.rarity, func.count()).where(Card.set_id == set_id).group_by(Card.rarity)).all()
    out = [{"code": code, "count": n, "rank": rank(row.game_id, code)} for code, n in found]
    return sorted(out, key=lambda r: r["rank"])


@router.get("/cards/search", response_model=list[CardOut])
def search_cards(q: str, game: str | None = None, limit: int = 50, s: Session = Depends(get_session)):
    stmt = select(Card).join(CardSet).where(Card.name.ilike(f"%{q}%"))
    if game:
        stmt = stmt.where(CardSet.game_id == game)
    cards = list(s.exec(stmt.limit(min(limit, 200))))
    owned = owned_by_card(s)
    return [CardOut(**c.model_dump(include=set(CardOut.model_fields) - {"owned_quantity"}), owned_quantity=owned.get(c.id, 0)) for c in cards]
