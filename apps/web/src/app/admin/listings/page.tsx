"use client";

import Link from "next/link";
import { ChangeEvent, FormEvent, useEffect, useState } from "react";

import { formatDateTime, formatListingPrice } from "@/lib/locale";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE;
const TOKEN_KEY = "nicherides_access_token";

type MeResponse = {
  role: string;
};

type AdminListing = {
  id: number;
  status: string;
  owner_id: number;
  owner_label: string | null;
  title: string;
  make: string;
  model: string;
  year: number;
  city: string;
  price: number | null;
  photo_count: number;
  created_at: string;
  published_at: string | null;
};

type AdminListingResponse = {
  page: number;
  page_size: number;
  total: number;
  items: AdminListing[];
};

const STATUS_OPTIONS = [
  ["", "All statuses"],
  ["draft", "Draft"],
  ["pending_review", "Pending review"],
  ["active", "Active"],
  ["sold", "Sold"],
  ["rejected", "Rejected"],
  ["expired", "Archived"],
] as const;

async function parseApiError(res: Response): Promise<string> {
  const contentType = res.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await res.json() : await res.text();
  const detail = typeof payload === "string" ? payload : payload?.detail;
  return detail || `Failed with status ${res.status}`;
}

export default function AdminListingsPage() {
  const [listings, setListings] = useState<AdminListing[]>([]);
  const [status, setStatus] = useState("");
  const [query, setQuery] = useState("");
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [authorized, setAuthorized] = useState<boolean | null>(null);
  const [error, setError] = useState("");

  async function loadListings(nextStatus = status, nextQuery = query) {
    setError("");
    if (!API_BASE) {
      setError("NEXT_PUBLIC_API_BASE is missing.");
      setLoading(false);
      return;
    }

    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setAuthorized(false);
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const meRes = await fetch(`${API_BASE}/v1/me`, {
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store",
      });
      if (!meRes.ok) {
        setAuthorized(false);
        return;
      }
      const me = (await meRes.json()) as MeResponse;
      if (me.role !== "admin") {
        setAuthorized(false);
        return;
      }
      setAuthorized(true);

      const qs = new URLSearchParams({ page_size: "100" });
      if (nextStatus) qs.set("status", nextStatus);
      if (nextQuery.trim()) qs.set("q", nextQuery.trim());
      const res = await fetch(`${API_BASE}/v1/admin/cars?${qs.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store",
      });
      if (!res.ok) {
        throw new Error(await parseApiError(res));
      }
      const data = (await res.json()) as AdminListingResponse;
      setListings(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load listings.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadListings();
  // Run once on mount; filters call loadListings directly.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleStatusFilter(event: ChangeEvent<HTMLSelectElement>) {
    const nextStatus = event.target.value;
    setStatus(nextStatus);
    void loadListings(nextStatus, query);
  }

  function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void loadListings(status, query);
  }

  async function deleteListing(listing: AdminListing) {
    if (!API_BASE) {
      setError("NEXT_PUBLIC_API_BASE is missing.");
      return;
    }
    const confirmed = window.confirm(
      `Permanently delete listing #${listing.id} "${listing.title}"? This removes its photos, offers, messages, reports, and related database records. This cannot be undone.`,
    );
    if (!confirmed) return;

    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setAuthorized(false);
      return;
    }

    setDeletingId(listing.id);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/v1/admin/cars/${listing.id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        throw new Error(await parseApiError(res));
      }
      setListings((current) => current.filter((item) => item.id !== listing.id));
      setTotal((current) => Math.max(0, current - 1));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete listing.");
    } finally {
      setDeletingId(null);
    }
  }

  if (authorized === false) {
    return (
      <main className="page shell">
        <section className="panel">
          <h1 className="subheading">Admin listings</h1>
          <p className="notice error">Admin access required.</p>
          <Link href="/login" className="btn btn-primary">Login</Link>
        </section>
      </main>
    );
  }

  return (
    <main className="page shell">
      <section className="panel">
        <div className="results-bar">
          <div>
            <h1 className="subheading">Admin listings</h1>
            <p>{total} listing{total === 1 ? "" : "s"} found.</p>
          </div>
          <Link href="/admin/reports" className="btn btn-secondary">View reports</Link>
        </div>

        <form className="form-grid form-grid-2 spaced-top-sm" onSubmit={handleSearch}>
          <div>
            <label className="label" htmlFor="admin-listing-search">Search</label>
            <input
              id="admin-listing-search"
              className="input"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Title, make, model, or city"
            />
          </div>
          <div>
            <label className="label" htmlFor="admin-listing-status">Status</label>
            <select id="admin-listing-status" className="select" value={status} onChange={handleStatusFilter}>
              {STATUS_OPTIONS.map(([value, label]) => (
                <option key={value || "all"} value={value}>{label}</option>
              ))}
            </select>
          </div>
          <button type="submit" className="btn btn-secondary" disabled={loading}>Search</button>
        </form>

        {error ? <p className="notice error spaced-top-sm">{error}</p> : null}
        {loading ? <p className="helper-text spaced-top-sm">Loading listings...</p> : null}

        {!loading && listings.length === 0 ? (
          <div className="empty-state">
            <h3>No listings found</h3>
            <p>Try another search or status.</p>
          </div>
        ) : null}

        <div className="listing-grid spaced-top-sm">
          {listings.map((listing) => (
            <article key={listing.id} className="panel panel-soft">
              <div className="results-bar">
                <div>
                  <p className="hero-kicker">Listing #{listing.id} · {listing.status.replaceAll("_", " ")}</p>
                  <h2 className="subheading">{listing.year} {listing.make} {listing.model}</h2>
                  <p className="car-meta">{listing.title}</p>
                </div>
                <Link href={`/cars/${listing.id}`} className="btn btn-secondary">Open listing</Link>
              </div>

              <div className="specs spaced-top-sm">
                <article className="spec">
                  <p className="spec-key">Owner</p>
                  <p className="spec-val">{listing.owner_label || `#${listing.owner_id}`}</p>
                </article>
                <article className="spec">
                  <p className="spec-key">City</p>
                  <p className="spec-val">{listing.city}</p>
                </article>
                <article className="spec">
                  <p className="spec-key">Price</p>
                  <p className="spec-val">{formatListingPrice(listing.price, "en")}</p>
                </article>
                <article className="spec">
                  <p className="spec-key">Photos</p>
                  <p className="spec-val">{listing.photo_count}</p>
                </article>
                <article className="spec">
                  <p className="spec-key">Created</p>
                  <p className="spec-val">{formatDateTime(listing.created_at, "en")}</p>
                </article>
              </div>

              <div className="contact-actions spaced-top-sm">
                <button
                  type="button"
                  className="btn btn-danger"
                  disabled={deletingId === listing.id}
                  onClick={() => void deleteListing(listing)}
                >
                  {deletingId === listing.id ? "Deleting..." : "Delete permanently"}
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
