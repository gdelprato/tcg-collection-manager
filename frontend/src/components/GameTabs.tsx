import { GAMES, type Game } from "../api";

export default function GameTabs({ value, onChange }: { value: Game; onChange: (g: Game) => void }) {
  return (
    <div className="seg" role="group" aria-label="Gioco">
      {GAMES.map((g) => (
        <button key={g.id} aria-pressed={value === g.id} onClick={() => onChange(g.id)}>
          {g.label}
        </button>
      ))}
    </div>
  );
}
