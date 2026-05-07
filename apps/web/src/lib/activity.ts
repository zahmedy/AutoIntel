"use client";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE;
const TOKEN_KEY = "nicherides_access_token";
const SESSION_KEY = "nicherides_activity_session";

type ActivityPayload = {
  carId?: number | string | null;
  source?: string;
  path?: string;
  searchQuery?: string | null;
  filters?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
};

function randomId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
}

export function activitySessionId(): string {
  const existing = localStorage.getItem(SESSION_KEY);
  if (existing) return existing;

  const next = randomId();
  localStorage.setItem(SESSION_KEY, next);
  return next;
}

export function trackActivity(eventType: string, payload: ActivityPayload = {}) {
  if (!API_BASE || typeof window === "undefined") return;

  const token = localStorage.getItem(TOKEN_KEY);
  const carId = Number(payload.carId);
  const body = {
    event_type: eventType,
    session_id: activitySessionId(),
    car_id: Number.isFinite(carId) ? carId : undefined,
    source: payload.source,
    path: payload.path ?? `${window.location.pathname}${window.location.search}`,
    search_query: payload.searchQuery || undefined,
    filters: payload.filters ?? {},
    metadata: payload.metadata ?? {},
  };

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  fetch(`${API_BASE}/v1/activity/events`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
    keepalive: true,
  }).catch(() => {
    // Analytics must never block the buying/selling flow.
  });
}
