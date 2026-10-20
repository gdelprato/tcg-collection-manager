# CLAUDE.md

Web app personale per gestire collezioni di carte collezionabili (Pokémon, inclusi set giapponesi, e Magic). Un solo utente, nessuna autenticazione, niente prezzi. Spec e roadmap in `docs/SPEC.md`.

## Struttura

- `backend/` — FastAPI + SQLModel su SQLite
  - `app/models.py` modello dati agnostico rispetto al gioco (Game, CardSet, Card, CollectionItem)
  - `app/adapters/` una classe per fonte di catalogo: `tcgdex.py` (Pokémon), `scryfall.py` (Magic). Il parsing è in funzioni pure, la rete passa solo da `CachedClient`
  - `app/rarity.py` normalizzazione delle rarità per gioco
  - `app/importer.py` upsert idempotente di set e carte
  - `app/routers/` API: `catalog.py` (set, carte, ricerca), `collection.py` (copie possedute), `imports.py` (catalogo remoto e import)
  - `app/cli.py` import da riga di comando
  - `tests/` pytest con fixture JSON in `tests/fixtures/`, nessuna chiamata di rete
- `frontend/` — React 18 + TypeScript + Vite, react-router. Chiamate API in `src/api.ts`, pagine in `src/pages/`

## Comandi

```bash
cd backend && pytest                          # test backend
cd backend && uvicorn app.main:app --reload   # API :8000, docs su /docs
cd backend && python -m app.cli import pokemon SV2a --lang ja
cd frontend && npm run dev                    # UI :5173, proxy /api -> :8000
cd frontend && npm run build                  # type-check + build
```

## Convenzioni

- Aggiungere un gioco = nuovo adapter in `app/adapters/` registrato in `ADAPTERS`, tabella rarità in `rarity.py`, fixture e test. Nessun campo specifico di un gioco nei modelli: se serve, prima discuterne.
- Il numero carta è sempre una stringa (`"064"`, `"138★"`); ordinare con `sort_key`.
- Lo stesso set in lingue diverse è un `CardSet` separato.
- Rispettare i limiti delle API gratuite: niente chiamate fuori da `CachedClient`, niente loop di richieste senza intervallo.
- Testi dell'interfaccia e messaggi di errore delle API in italiano; codice, nomi e commenti in inglese.
- Ogni modifica al backend arriva con test; i test non devono mai usare la rete.
- Frontend: niente librerie UI per ora, CSS in `src/styles.css` con variabili per tema chiaro e scuro.

## Stato

Scaffold iniziale testato offline. Prima cosa da fare con la rete disponibile: i punti di "Da verificare per primo" in `docs/SPEC.md`.

## Agenti Claude Code

Definiti in `.claude/agents/`, da invocare per nome:

| Agente | Uso |
|---|---|
| `roadmap-planner` | Sola lettura. Piano di una voce della roadmap prima di iniziare un branch |
| `backend-dev` | API, modelli, importer, CLI e test in `backend/` |
| `catalog-adapter` | Adapter delle fonti (TCGdex, Scryfall, nuovi giochi), `rarity.py`, fixture |
| `frontend-dev` | Pagine, componenti, `api.ts`, `styles.css` in `frontend/` |
| `code-reviewer` | Sola lettura. Revisione del diff contro queste convenzioni, esegue test e build |

Flusso tipico: `roadmap-planner` → `backend-dev` / `catalog-adapter` → `frontend-dev` → `code-reviewer` → PR verso `main`.

`.claude/settings.json` pre-autorizza test, build e le API dei cataloghi; `.claude/hooks/session-start.sh` installa le dipendenze nelle sessioni cloud.

## Branch

Un branch per voce della roadmap, sempre con PR verso `main`:

- `chore/verify-live-apis` — "Da verificare per primo" in `docs/SPEC.md`
- `feature/collection-page` — roadmap 2
- `feature/wishlist-missing` — roadmap 3
- `feature/csv-import-export` — roadmap 4
- `feature/card-images` — roadmap 5
- `feature/import-performance` — roadmap 6
- `feature/photo-recognition` — roadmap 7
