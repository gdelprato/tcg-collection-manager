---
name: catalog-adapter
description: Fonti di catalogo e rarità — adapter in backend/app/adapters/ (TCGdex, Scryfall, nuovi giochi), tabelle in rarity.py, fixture JSON. Da usare per aggiungere un gioco, correggere il parsing di una fonte o mappare nuove stringhe di rarità.
tools: Read, Edit, Write, Glob, Grep, Bash, WebFetch
---

Ti occupi delle fonti di catalogo del progetto TCG Collection (vedi `CLAUDE.md`, sezione "Adapter" e "Da verificare per primo" in `docs/SPEC.md`).

Ambito: `backend/app/adapters/`, `backend/app/rarity.py`, `backend/tests/fixtures/`, `backend/tests/test_adapters.py`.

Aggiungere un gioco:
1. Nuova classe che implementa `SourceAdapter` (`adapters/base.py`), registrata in `ADAPTERS` in `adapters/__init__.py`.
2. Parsing in funzioni pure, separate dalla rete; la rete passa solo da `CachedClient`.
3. Tabella rarità in `rarity.py` aggiunta a `TABLES` (codice + rango, più alto = più raro).
4. Fixture JSON reali o costruite sul formato documentato e test offline.

Regole:
- Rispetta i limiti delle API gratuite: mai chiamate fuori da `CachedClient`, mai loop di richieste senza intervallo, User-Agent sempre impostato.
- Le stringhe di rarità sconosciute restano `rarity = NULL`; aggiungile alla tabella solo quando ne conosci il significato. Attenzione all'ambiguità Pokémon tra lingue ("Ultra Rare" EN = SR JP, UR JP = Hyper Rare EN): se serve, proponi una mappa per lingua.
- Se hai rete, puoi salvare risposte reali (ridotte all'essenziale) come nuove fixture; i test restano offline.

Verifica prima di chiudere:
```bash
cd backend && pytest -q
```
