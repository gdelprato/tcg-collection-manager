"""Command line import, e.g.:
    python -m app.cli sets pokemon --lang ja
    python -m app.cli import pokemon SV2a --lang ja
    python -m app.cli import magic mkm
    python -m app.cli rarities          # raw rarity strings not yet mapped in rarity.py
"""

import argparse

from sqlmodel import Session, select

from .adapters import ADAPTERS
from .db import engine, init_db
from .importer import import_set
from .models import Card, CardSet


def main() -> None:
    p = argparse.ArgumentParser(prog="tcg")
    sub = p.add_subparsers(dest="cmd", required=True)
    ls = sub.add_parser("sets", help="list remote sets")
    ls.add_argument("game", choices=ADAPTERS)
    ls.add_argument("--lang", default="en")
    imp = sub.add_parser("import", help="import one or more sets")
    imp.add_argument("game", choices=ADAPTERS)
    imp.add_argument("set_ids", nargs="+")
    imp.add_argument("--lang", default="en")
    sub.add_parser("rarities", help="show unmapped raw rarities")
    a = p.parse_args()

    init_db()
    if a.cmd == "sets":
        for x in ADAPTERS[a.game](language=a.lang).list_sets():
            print(f"{x.source_id:<14} {x.name}  ({x.card_count or '?'} carte)")
    elif a.cmd == "import":
        adapter = ADAPTERS[a.game](language=a.lang)
        with Session(engine) as s:
            for sid in a.set_ids:
                row = import_set(s, adapter, adapter.get_set(sid))
                print(f"Importato {row.code} {row.name}: {row.card_count} carte")
    elif a.cmd == "rarities":
        with Session(engine) as s:
            rows = s.exec(select(CardSet.game_id, Card.rarity_raw).join(CardSet).where(Card.rarity.is_(None)).distinct())
            for game, raw in rows:
                print(f"{game}: {raw!r}")


if __name__ == "__main__":
    main()
