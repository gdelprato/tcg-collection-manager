import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("TCG_DATA_DIR", Path(__file__).resolve().parent.parent / "data"))
DB_URL = os.environ.get("TCG_DB_URL", f"sqlite:///{DATA_DIR / 'collection.db'}")
CACHE_DIR = DATA_DIR / "cache"
# Scryfall requires an identifying User-Agent and an Accept header on every request.
USER_AGENT = os.environ.get("TCG_USER_AGENT", "tcg-collection/0.1 (personal project)")
