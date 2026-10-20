from app.importer import import_set

from .conftest import FakeScryfall, FakeTCGdex


def seed(session):
    a = FakeTCGdex()
    pkm = import_set(session, a, a.get_set("SV2a"))
    m = FakeScryfall()
    from app.adapters.base import SetData
    mtg = import_set(session, m, SetData(source_id="mh2", code="MH2", name="Modern Horizons 2"))
    return pkm, mtg


def test_import_is_idempotent(session):
    pkm, _ = seed(session)
    pkm2, _ = seed(session)
    assert pkm.id == pkm2.id and pkm2.card_count == 210


def test_sets_and_checklist_flow(client, session):
    pkm, mtg = seed(session)
    sets = client.get("/api/sets", params={"game": "pokemon"}).json()
    assert [s["code"] for s in sets] == ["SV2a"] and sets[0]["imported"] == 3

    detail = client.get(f"/api/sets/{pkm.id}", params={"rarity": "AR,SAR"}).json()
    assert [c["rarity"] for c in detail["cards"]] == ["AR", "SAR"]

    pika = detail["cards"][0]["id"]
    assert client.put(f"/api/collection/cards/{pika}", json={"quantity": 2}).json()["owned_quantity"] == 2
    assert client.get(f"/api/sets/{pkm.id}").json()["owned"] == 1
    assert client.get("/api/sets", params={"game": "pokemon"}).json()[0]["owned"] == 1

    item = client.post("/api/collection", json={"card_id": pika, "finish": "reverse", "grading": "PSA 10"}).json()
    assert client.get("/api/collection/stats").json() == [{"game": "pokemon", "distinct_cards": 1, "copies": 3}]
    assert client.patch(f"/api/collection/{item['id']}", json={"condition": "LP"}).json()["condition"] == "LP"

    assert client.put(f"/api/collection/cards/{pika}", json={"quantity": 0}).json()["owned_quantity"] == 0
    assert client.get("/api/collection").json() == []


def test_search_and_rarities(client, session):
    pkm, _ = seed(session)
    assert [c["name"] for c in client.get("/api/cards/search", params={"q": "bolt"}).json()] == ["Lightning Bolt"]
    codes = [r["code"] for r in client.get(f"/api/sets/{pkm.id}/rarities").json()]
    assert codes == ["C", "AR", "SAR"]
