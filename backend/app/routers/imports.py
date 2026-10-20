from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..adapters import ADAPTERS
from ..db import get_session
from ..importer import import_set
from ..schemas import ImportIn

router = APIRouter(prefix="/api/sources", tags=["import"])


def adapter_for(game: str, language: str):
    cls = ADAPTERS.get(game)
    if not cls:
        raise HTTPException(400, f"Gioco non supportato: {game}")
    return cls(language=language)


@router.get("/{game}/sets")
def remote_sets(game: str, language: str = "en") -> list[dict]:
    """Sets available in the remote catalogue (not yet necessarily imported)."""
    return [vars(x) for x in adapter_for(game, language).list_sets()]


@router.post("/import")
def import_remote_set(body: ImportIn, s: Session = Depends(get_session)) -> dict:
    adapter = adapter_for(body.game, body.language)
    row = import_set(s, adapter, adapter.get_set(body.set_id))
    return {"id": row.id, "code": row.code, "name": row.name, "card_count": row.card_count}
