import { apiRequest } from "./client";
import { getToken } from "../auth/token";

export type Journal = {
  journal_id: number;
  user_id: number;
  symbol: string;
  side: "buy" | "sell";
  price: number;
  quantity: number;
  note?: string | null;
  exit_price?: number | null;
  exit_time?: string | null;
  pnl?: number | null;
  created_at: string;
};

export type JournalFilters = {
  symbol?: string;
  status?: "open" | "closed";
  start_date?: string;
  end_date?: string;
  side?: "buy" | "sell";
};

export async function fetchJournals(filters: JournalFilters = {}) {
  const userId = Number(getToken());
  const params = new URLSearchParams();
  params.set("user_id", String(userId));
  if (filters.symbol) params.set("symbol", filters.symbol);
  if (filters.status) params.set("status", filters.status);
  if (filters.start_date) params.set("start_date", filters.start_date);
  if (filters.end_date) params.set("end_date", filters.end_date);
  if (filters.side) params.set("side", filters.side);
  return apiRequest<Journal[]>(`/journals?${params.toString()}`, "GET");
}

export async function createJournal(input: {
  symbol: string;
  side: "buy" | "sell";
  price: number;
  quantity: number;
  note?: string;
}) {
  const user_id = Number(getToken());
  return apiRequest<{ message: string; journal_id: number }>(`/journals`, "POST", {
    user_id,
    ...input,
  });
}

export async function deleteJournal(journal_id: number) {
  const user_id = Number(getToken());
  return apiRequest<{ message: string }>(`/journals/${journal_id}`, "DELETE", {
    user_id,
  });
}

export async function closeJournal(journal_id: number, exit_price: number) {
  const user_id = Number(getToken());
  return apiRequest<{ message: string; pnl: number }>(
    `/journals/${journal_id}/close`,
    "POST",
    { user_id, exit_price }
  );
}

