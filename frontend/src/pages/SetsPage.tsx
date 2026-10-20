import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, type CardSet, type Game } from "../api";
import GameTabs from "../components/GameTabs";

export default function SetsPage() {
  const [params, setParams] = useSearchParams();
  const game = (params.get("game") as Game) || "pokemon";
  const [sets, setSets] = useState<CardSet[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSets(null);
    api.sets(game).then(setSets).catch((e) => setError(e.message));
  }, [game]);

  return (
    <>
      <div className="pagehead">
        <h1>I tuoi set</h1>
        <GameTabs value={game} onChange={(g) => setParams({ game: g })} />
      </div>
      {error && <p className="error">{error}</p>}
      {sets && sets.length === 0 && (
        <p className="empty">
          Nessun set importato per questo gioco. <Link to="/import">Importa il primo set</Link>.
        </p>
      )}
      <ul className="setgrid">
        {sets?.map((s) => {
          const pct = s.imported ? Math.round((s.owned / s.imported) * 100) : 0;
          return (
            <li key={s.id}>
              <Link to={`/sets/${s.id}`} className="setcard">
                <span className="code">{s.code} · {s.language.toUpperCase()}</span>
                <span className="setname">{s.name}</span>
                <span className="meta">
                  {s.release_date ?? "data n.d."} · {s.owned}/{s.imported} carte
                </span>
                <span className="prog"><i style={{ width: `${pct}%` }} /></span>
              </Link>
            </li>
          );
        })}
      </ul>
    </>
  );
}
