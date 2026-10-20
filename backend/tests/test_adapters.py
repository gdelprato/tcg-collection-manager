from app.adapters import scryfall, tcgdex
from app.adapters.base import sort_key
from app.rarity import normalize

from .conftest import FakeScryfall, FakeTCGdex, load


def test_tcgdex_set_parsing():
    s = tcgdex.parse_set(load("tcgdex_set.json"))
    assert (s.source_id, s.official_count, s.card_count, s.series) == ("SV2a", 165, 210, "Scarlet & Violet")
    assert s.release_date.isoformat() == "2023-06-16"


def test_tcgdex_cards_have_rarity_and_image():
    cards = FakeTCGdex().fetch_cards("SV2a")
    assert [c.rarity_raw for c in cards] == ["Common", "Art Rare", "Special Art Rare"]
    assert cards[1].image_url == "https://assets.tcgdex.net/ja/SV/SV2a/173/high.webp"


def test_scryfall_double_faced_image_and_numbers():
    cards = FakeScryfall().fetch_cards("mh2")
    assert cards[1].image_url.endswith("b2.jpg")
    assert cards[2].number == "138★" and sort_key(cards[2].number) == 138


def test_scryfall_set_parsing():
    s = scryfall.parse_set({"code": "mh2", "name": "Modern Horizons 2", "set_type": "draft_innovation",
                            "released_at": "2021-06-18", "card_count": 491, "printed_size": 303})
    assert (s.code, s.official_count) == ("MH2", 303)


def test_rarity_normalization():
    assert normalize("pokemon", "Special Art Rare").code == "SAR"
    assert normalize("pokemon", "Illustration rare").code == "AR"
    assert normalize("magic", "mythic").code == "M"
    assert normalize("pokemon", "Something new") is None
