"use client";

import { FormEvent, useEffect, useState } from "react";
import { ReviewCard, type ReviewItem } from "@/components/ReviewCard";
import { api } from "@/lib/api";
import { NOTICES } from "@/components/Footer";

export default function HomePage() {
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [q, setQ] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function load(event?: FormEvent) {
    event?.preventDefault();
    try {
      if (q) {
        const body = await api<{ reviews: ReviewItem[] }>(`/api/v1/search?q=${encodeURIComponent(q)}`);
        setItems(body.reviews);
      } else {
        const body = await api<{ items: ReviewItem[] }>("/api/v1/feed");
        setItems(body.items);
      }
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load feed.");
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-8">
      <section className="space-y-3">
        <p className="text-xs uppercase tracking-[0.2em] text-orange-700">Invitation-only product discovery</p>
        <h1 className="serif text-4xl">Honest reviews across everyday products.</h1>
        <p className="max-w-2xl text-slate-600">
          The public feed shows only published reviews. Drafts and anything still in review stay invisible.
        </p>
      </section>
      <form onSubmit={load} className="flex gap-3 rounded-2xl border border-slate-200 bg-white p-4">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search products, reviews, usernames"
          className="flex-1 rounded-lg border border-slate-200 px-3 py-2"
        />
        <button type="submit" className="rounded-lg bg-teal-700 px-4 py-2 text-white">
          Search
        </button>
      </form>
      {error ? <p className="text-sm text-red-700">{error}</p> : null}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((review) => (
          <ReviewCard key={review.id} review={review} />
        ))}
      </div>
      <p className="text-xs text-slate-500">{NOTICES.general}</p>
    </div>
  );
}
