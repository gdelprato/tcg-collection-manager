import json
import os
import tempfile
from pathlib import Path

os.environ.setdefault("TCG_DATA_DIR", tempfile.mkdtemp(prefix="tcg-test-"))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402
from sqlmodel.pool import StaticPool  # noqa: E402

from app import db  # noqa: E402
from app.adapters import scryfall, tcgdex  # noqa: E402
from app.main import app  # noqa: E402

FIX = Path(__file__).parent / "fixtures"


def load(name):
    return json.loads((FIX / name).read_text())


class FakeTCGdex(tcgdex.TCGdexAdapter):
    """TCGdex adapter reading fixtures instead of the network."""

    def __init__(self, language="ja"):
        self.language = language
        set_json, cards = load("tcgdex_set.json"), load("tcgdex_cards.json")

        class Client:
            def get_json(self, url, use_cache=True):
                last = url.rsplit("/", 1)[-1]
                return set_json if "/sets/" in url else cards[last]

        self.client = Client()


class FakeScryfall(scryfall.ScryfallAdapter):
    def __init__(self, language="en"):
        self.language = language
        page = load("scryfall_search.json")

        class Client:
            def get_json(self, url, use_cache=True):
                return page

        self.client = Client()


@pytest.fixture()
def engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(eng)
    db.init_db(eng)
    return eng


@pytest.fixture()
def session(engine):
    with Session(engine) as s:
        yield s


@pytest.fixture()
def client(engine):
    def override():
        with Session(engine) as s:
            yield s

    app.dependency_overrides[db.get_session] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
