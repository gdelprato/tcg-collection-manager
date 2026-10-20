export type Game = "pokemon" | "magic";

export interface CardSet {
  id: number;
  game_id: Game;
  code: string;
  name: string;
  series: string | null;
  language: string;
  release_date: string | null;
  card_count: number | null;
  official_count: number | null;
  logo_url: string | null;
  imported: number;
  owned: number;
}

export interface Card {
  id: number;
  number: string;
  name: string;
  rarity: string | null;
  rarity_raw: string | null;
  image_url: string | null;
  owned_quantity: number;
}

export interface SetDetail extends CardSet {
  cards: Card[];
}

export interface RemoteSet {
  source_id: string;
  code: string;
  name: string;
  card_count: number | null;
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Errore ${res.status}`);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

export const api = {
  sets: (game: Game) => req<CardSet[]>(`/api/sets?game=${game}`),
  set: (id: number) => req<SetDetail>(`/api/sets/${id}`),
  setQuantity: (cardId: number, quantity: number) =>
    req<{ owned_quantity: number }>(`/api/collection/cards/${cardId}`, {
      method: "PUT",
      body: JSON.stringify({ quantity }),
    }),
  remoteSets: (game: Game, language: string) =>
    req<RemoteSet[]>(`/api/sources/${game}/sets?language=${language}`),
  importSet: (game: Game, setId: string, language: string) =>
    req<{ id: number; code: string; name: string }>(`/api/sources/import`, {
      method: "POST",
      body: JSON.stringify({ game, set_id: setId, language }),
    }),
  stats: () => req<{ game: Game; distinct_cards: number; copies: number }[]>(`/api/collection/stats`),
};

export const GAMES: { id: Game; label: string; languages: string[] }[] = [
  { id: "pokemon", label: "Pokémon", languages: ["ja", "en", "it"] },
  { id: "magic", label: "Magic", languages: ["en", "it", "ja"] },
];
