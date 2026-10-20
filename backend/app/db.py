from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from .config import DATA_DIR, DB_URL

DATA_DIR.mkdir(parents=True, exist_ok=True)
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})


def init_db(eng=engine) -> None:
    from . import models  # noqa: F401  (register tables)

    SQLModel.metadata.create_all(eng)
    with Session(eng) as s:
        for gid, name in (("pokemon", "Pokémon"), ("magic", "Magic: The Gathering")):
            if not s.get(models.Game, gid):
                s.add(models.Game(id=gid, name=name))
        s.commit()


def get_session() -> Iterator[Session]:
    with Session(engine) as s:
        yield s
