"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { ReviewCard, type ReviewItem } from "@/components/ReviewCard";
import { api } from "@/lib/api";

type Product = { id: string; name: string; brand_name: string };
type UserHit = { username: string; display_name: string | null };

export default function SearchPage() {
  const [q, setQ] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  const [users, setUsers] = useState<UserHit[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function run(event?: FormEvent) {
    event?.preventDefault();
    if (!q.trim()) return;
    try {
      const data = await api<{ products: Product[]; reviews: ReviewItem[]; users: UserHit[] }>(
        `/api/v1/search?q=${encodeURIComponent(q)}`,
      );
      setProducts(data.products);
      setReviews(data.reviews);
      setUsers(data.users);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed.");
    }
  }

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const initial = params.get("q");
    if (initial) {
      setQ(initial);
    }
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Search</h1>
      <form onSubmit={run} className="panel">
        {error ? <p className="text-sm text-red-400">{error}</p> : null}
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Product, brand, reviewer, or keyword" className="field" />
        <button type="submit" className="btn">
          Search
        </button>
      </form>
      {users.length ? (
        <section className="space-y-2">
          <h2 className="text-xl font-semibold">Reviewers</h2>
          {users.map((user) => (
            <Link key={user.username} href={`/users/${user.username}`} className="compact-card">
              @{user.username}
              {user.display_name ? <span className="muted block text-sm">{user.display_name}</span> : null}
            </Link>
          ))}
        </section>
      ) : null}
      {products.length ? (
        <section className="space-y-2">
          <h2 className="text-xl font-semibold">Products</h2>
          {products.map((product) => (
            <Link key={product.id} href={`/products/${product.id}`} className="compact-card">
              {product.brand_name} {product.name}
            </Link>
          ))}
        </section>
      ) : null}
      {reviews.length ? (
        <section className="space-y-2">
          <h2 className="text-xl font-semibold">Published reviews</h2>
          {reviews.map((review) => (
            <ReviewCard key={review.id} review={review} variant="compact" />
          ))}
        </section>
      ) : null}
    </div>
  );
}
