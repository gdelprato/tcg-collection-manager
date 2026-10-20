import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, GAMES, type Game, type RemoteSet } from "../api";
import GameTabs from "../components/GameTabs";

export default function ImportPage() {
  const [game, setGame] = useState<Game>("pokemon");
  const [language, setLanguage] = useState("ja");
  const [remote, setRemote] = useState<RemoteSet[] | null>(null);
  const [filter, setFilter] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const languages = GAMES.find((g) => g.id === game)!.languages;

  useEffect(() => {
    if (!languages.includes(language)) setLanguage(languages[0]);
  }, [game]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    setRemote(null);
    setError(null);
    api.remoteSets(game, language).then(setRemote).catch((e) => setError(e.message));
  }, [game, language]);

  async function run(s: RemoteSet) {
    setBusy(s.source_id);
    setError(null);
    try {
      const row = await api.importSet(game, s.source_id, language);
      navigate(`/sets/${row.id}`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  const shown = remote?.filter((s) => `${s.code} ${s.name}`.toLowerCase().includes(filter.toLowerCase()));

  return (
    <>
      <div className="pagehead">
        <h1>Importa un set</h1>
        <p className="meta">Scarica il catalogo di un set dalla fonte del gioco: TCGdex per Pokémon, Scryfall per Magic.</p>
      </div>
      <div className="bar">
        <GameTabs value={game} onChange={setGame} />
        <select value={language} onChange={(e) => setLanguage(e.target.value)} aria-label="Lingua">
          {languages.map((l) => <option key={l} value={l}>{l.toUpperCase()}</option>)}
        </select>
        <input type="search" placeholder="Filtra per nome o codice…" value={filter} onChange={(e) => setFilter(e.target.value)} aria-label="Filtra set" />
      </div>
      {error && <p className="error">{error}</p>}
      {!remote && !error && <p className="empty">Caricamento dell'elenco set…</p>}
      <ul className="remote">
        {shown?.map((s) => (
          <li key={s.source_id}>
            <span className="code">{s.code}</span>
            <span className="name">{s.name}</span>
            <span className="meta">{s.card_count ?? "?"} carte</span>
            <button disabled={busy !== null} onClick={() => run(s)}>
              {busy === s.source_id ? "Importazione…" : "Importa"}
            </button>
          </li>
        ))}
      </ul>
    </>
  );
}
