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
