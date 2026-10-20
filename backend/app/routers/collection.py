from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select

from ..db import get_session
from ..models import Card, CardSet, CollectionItem
from ..schemas import ItemIn, ItemPatch, QuantityIn

router = APIRouter(prefix="/api/collection", tags=["collection"])


@router.get("")
def list_items(game: str | None = None, s: Session = Depends(get_session)) -> list[dict]:
    stmt = select(CollectionItem, Card, CardSet).join(Card, Card.id == CollectionItem.card_id).join(CardSet, CardSet.id == Card.set_id)
    if game:
        stmt = stmt.where(CardSet.game_id == game)
    return [
        {**i.model_dump(), "card": {"name": c.name, "number": c.number, "rarity": c.rarity, "image_url": c.image_url},
         "set": {"id": st.id, "code": st.code, "name": st.name, "game_id": st.game_id, "language": st.language}}
        for i, c, st in s.exec(stmt.order_by(CardSet.release_date.desc(), Card.sort_key))
    ]


@router.post("", status_code=201)
def add_item(body: ItemIn, s: Session = Depends(get_session)) -> CollectionItem:
    if not s.get(Card, body.card_id):
        raise HTTPException(404, "Carta non trovata")
    item = CollectionItem(**body.model_dump())
    s.add(item)
    s.commit()
    s.refresh(item)
    return item


@router.patch("/{item_id}")
def update_item(item_id: int, body: ItemPatch, s: Session = Depends(get_session)) -> CollectionItem:
    item = s.get(CollectionItem, item_id)
    if not item:
        raise HTTPException(404, "Elemento non trovato")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    s.add(item)
    s.commit()
    s.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, s: Session = Depends(get_session)) -> None:
    item = s.get(CollectionItem, item_id)
    if not item:
        raise HTTPException(404, "Elemento non trovato")
    s.delete(item)
    s.commit()


@router.put("/cards/{card_id}")
def set_quantity(card_id: int, body: QuantityIn, s: Session = Depends(get_session)) -> dict:
    """Checklist shortcut: set the total quantity of a card (normal finish, NM).
    0 removes every copy of that card; detailed items are managed via the endpoints above."""
    if not s.get(Card, card_id):
        raise HTTPException(404, "Carta non trovata")
    items = list(s.exec(select(CollectionItem).where(CollectionItem.card_id == card_id)))
    if body.quantity == 0:
        for i in items:
            s.delete(i)
    else:
        other = sum(i.quantity for i in items[1:])
        if items:
            items[0].quantity = max(1, body.quantity - other)
            s.add(items[0])
        else:
            s.add(CollectionItem(card_id=card_id, quantity=body.quantity))
    s.commit()
    total = s.exec(select(func.sum(CollectionItem.quantity)).where(CollectionItem.card_id == card_id)).one()
    return {"card_id": card_id, "owned_quantity": int(total or 0)}


@router.get("/stats")
def stats(s: Session = Depends(get_session)) -> list[dict]:
    rows = s.exec(
        select(CardSet.game_id, func.count(func.distinct(Card.id)), func.sum(CollectionItem.quantity))
        .join(Card, Card.id == CollectionItem.card_id)
        .join(CardSet, CardSet.id == Card.set_id)
        .group_by(CardSet.game_id)
    ).all()
    return [{"game": g, "distinct_cards": d, "copies": int(c or 0)} for g, d, c in rows]
