# Specifica e roadmap

## Obiettivo

Gestire la propria collezione di carte di più giochi in un'unica app: scegliere i set, vedere la checklist completa con le rarità, segnare cosa si possiede e quante copie. Uso personale, un solo utente, nessuna autenticazione. I prezzi sono fuori scope.

## Modello dati

| Tabella | Contenuto |
|---|---|
| `game` | Giochi supportati (`pokemon`, `magic`) |
| `card_set` | Set importati. Chiave logica: gioco + id nella fonte + lingua. Lo stesso set in giapponese e in inglese sono due righe distinte, perché numerazione e rarità cambiano |
| `card` | Carte del catalogo. `number` è il numero stampato (stringa: "064", "138★"), `sort_key` la sua parte numerica per l'ordinamento. `rarity_raw` è la stringa della fonte, `rarity` il codice normalizzato |
| `collection_item` | Copie possedute: carta, quantità, finitura (normal/holo/reverse/foil), condizione (NM…DMG), gradazione, note |

Le rarità non sono confrontabili tra giochi: `app/rarity.py` ha una tabella per gioco che mappa la stringa della fonte su codice + rango. Le stringhe sconosciute restano con `rarity = NULL`; `python -m app.cli rarities` le elenca.

## Adapter

Ogni fonte implementa `SourceAdapter` (`app/adapters/base.py`): `list_sets()`, `get_set(id)`, `fetch_cards(id)`. Il parsing sta in funzioni pure testate su fixture JSON. Le richieste passano da `CachedClient`, che rispetta un intervallo minimo tra le chiamate e salva le risposte su disco per 24 ore.

- **TCGdex** (`/v2/{lang}/sets`, `/sets/{id}`, `/cards/{id}`): l'endpoint del set non restituisce la rarità, quindi serve una richiesta per carta (cache inclusa).
- **Scryfall** (`/sets`, `/cards/search?q=e:{code} lang:{lang}&unique=prints`): paginato con `next_page`, richiede User-Agent e Accept, 50–100 ms tra le richieste.

## Da verificare per primo

Lo scaffold è stato scritto e testato senza accesso di rete alle due API: i test usano fixture costruite sul formato documentato.

1. Che TCGdex in giapponese (`ja`) copra i set SV e Mega con gli id attesi (`SV2a`, `M1L`…): `python -m app.cli sets pokemon --lang ja`.
2. Le stringhe di rarità reali di TCGdex per i set giapponesi: importare un set e lanciare `python -m app.cli rarities`, poi completare `POKEMON` in `rarity.py`. Attenzione all'ambiguità tra "Ultra Rare" inglese (= SR giapponese) e UR giapponese (= Hyper Rare inglese): potrebbe servire una mappa per lingua.
3. Salvare risposte reali come nuove fixture in `backend/tests/fixtures/`.

## Roadmap

1. **MVP** (questo scaffold): import per set, checklist con filtro rarità, quantità per carta.
2. Pagina collezione: elenco copie con finitura/condizione/gradazione, modifica dettagliata, statistiche per gioco e per set.
3. Wishlist e vista "mancanti" trasversale ai set (es. tutte le SAR che mancano).
4. Import/export CSV della collezione.
5. Immagini delle carte nella checklist (griglia a miniature, già presente `image_url`).
6. Performance import: GraphQL di TCGdex per un set intero in una chiamata; bulk data di Scryfall per l'intero catalogo.
7. Riconoscimento carta da foto: embedding delle immagini del catalogo (CLIP o simili), indice vettoriale locale, ricerca per similarità per aggiungere carte scattando una foto.
