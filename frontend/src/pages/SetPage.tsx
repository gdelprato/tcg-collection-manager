import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type Card, type SetDetail } from "../api";

export default function SetPage() {
  const { id } = useParams();
  const [set, setSet] = useState<SetDetail | null>(null);
  const [rarities, setRarities] = useState<Set<string>>(new Set());
  const [onlyMissing, setOnlyMissing] = useState(false);
  const [q, setQ] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.set(Number(id)).then(setSet).catch((e) => setError(e.message));
  }, [id]);

  const available = useMemo(() => {
    const seen: string[] = [];
    set?.cards.forEach((c) => c.rarity && !seen.includes(c.rarity) && seen.push(c.rarity));
    return seen;
  }, [set]);

  if (error) return <p className="error">{error}</p>;
  if (!set) return <p className="empty">Caricamento…</p>;

  const cards = set.cards.filter(
    (c) =>
      (rarities.size === 0 || rarities.has(c.rarity ?? "")) &&
      (!onlyMissing || c.owned_quantity === 0) &&
      (!q || c.name.toLowerCase().includes(q.toLowerCase())),
  );
  const owned = set.cards.filter((c) => c.owned_quantity > 0).length;

  async function change(card: Card, qty: number) {
    const prev = set!;
    const next = { ...prev, cards: prev.cards.map((c) => (c.id === card.id ? { ...c, owned_quantity: qty } : c)) };
    setSet(next); // optimistic
    try {
      await api.setQuantity(card.id, qty);
    } catch (e) {
      setSet(prev);
      setError((e as Error).message);
    }
  }

  function toggleRarity(r: string) {
    const n = new Set(rarities);
    n.has(r) ? n.delete(r) : n.add(r);
    setRarities(n);
  }

  return (
    <>
      <Link to={`/?game=${set.game_id}`} className="back">← Tutti i set</Link>
      <div className="pagehead">
        <h1><span className="code">{set.code}</span> {set.name}</h1>
        <p className="meta">
          {set.release_date ?? "data n.d."} · {owned}/{set.cards.length} possedute
        </p>
      </div>
      <div className="bar">
        <div className="chips" role="group" aria-label="Rarità">
          {available.map((r) => (
            <button key={r} className={`chip r-${r}`} aria-pressed={rarities.has(r)} onClick={() => toggleRarity(r)}>
              {r}
            </button>
          ))}
        </div>
        <input type="search" placeholder="Cerca carta…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Cerca carta" />
        <label className="tog">
          <input type="checkbox" checked={onlyMissing} onChange={(e) => setOnlyMissing(e.target.checked)} /> Solo mancanti
        </label>
      </div>
      <ul className="cards">
        {cards.map((c) => (
          <li key={c.id} className={c.owned_quantity ? "own" : ""}>
            <button className="check" aria-pressed={c.owned_quantity > 0} onClick={() => change(c, c.owned_quantity ? 0 : 1)} aria-label={c.owned_quantity ? "Segna come mancante" : "Segna come posseduta"}>
              {c.owned_quantity ? "✓" : ""}
            </button>
            <span className="num">{c.number}</span>
            <span className="name" title={c.rarity_raw ?? undefined}>{c.name}</span>
            {c.rarity && <span className={`chip small r-${c.rarity}`}>{c.rarity}</span>}
            {c.owned_quantity > 0 && (
              <span className="qty">
                <button onClick={() => change(c, c.owned_quantity - 1)} aria-label="Una copia in meno">−</button>
                {c.owned_quantity}
                <button onClick={() => change(c, c.owned_quantity + 1)} aria-label="Una copia in più">+</button>
              </span>
            )}
          </li>
        ))}
      </ul>
      {cards.length === 0 && <p className="empty">Nessuna carta corrisponde ai filtri.</p>}
    </>
  );
}
