# TCG Collection

Web app personale per gestire collezioni di carte collezionabili: cataloghi dei set, checklist per rarità, copie possedute. Per ora Pokémon (anche set giapponesi) e Magic: The Gathering.

- **Backend**: Python 3.11+, FastAPI, SQLModel, SQLite (`backend/`)
- **Frontend**: React 18 + TypeScript + Vite (`frontend/`)
- **Cataloghi**: [TCGdex](https://tcgdex.dev) per Pokémon, [Scryfall](https://scryfall.com/docs/api) per Magic

## Avvio

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                                  # test offline con fixture
python -m app.cli import pokemon SV2a --lang ja   # importa un set
uvicorn app.main:app --reload           # API su http://localhost:8000 (docs su /docs)

# frontend (in un altro terminale)
cd frontend
npm install
npm run dev                             # http://localhost:5173, /api in proxy verso :8000
```

I set si importano anche dall'interfaccia, pagina **Importa**.

Il database e la cache delle risposte API stanno in `backend/data/` (ignorata da git). Variabili d'ambiente: `TCG_DATA_DIR`, `TCG_DB_URL`, `TCG_USER_AGENT`.

Vedi `docs/SPEC.md` per modello dati, decisioni e roadmap.
