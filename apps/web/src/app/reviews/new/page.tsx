"use client";

import { FormEvent, Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

function Form() {
  const { user, ready } = useAuth();
  const router = useRouter();
  const search = useSearchParams();
  const [products, setProducts] = useState<{ id: string; name: string; brand_name: string }[]>([]);
  const [productId, setProductId] = useState(search.get("product") ?? "");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [rating, setRating] = useState("5");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (ready && !user) router.push("/login");
  }, [ready, user, router]);
  useEffect(() => {
    api<{ items: { id: string; name: string; brand_name: string }[] }>("/api/v1/products").then((res) => setProducts(res.items));
  }, []);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      const review = await api<{ id: string }>("/api/v1/reviews", {
        method: "POST",
        body: JSON.stringify({
          product_id: productId,
          title,
          body,
          overall_rating: Number(rating),
          publish: false,
        }),
      });
      router.push(`/reviews/${review.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save.");
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="serif text-3xl">Write a review</h1>
      <form onSubmit={onSubmit} className="space-y-3 rounded-2xl border bg-white p-6">
        {error ? <p className="text-sm text-red-700">{error}</p> : null}
        <select required value={productId} onChange={(e) => setProductId(e.target.value)} className="w-full rounded-lg border px-3 py-2">
          <option value="">Select product</option>
          {products.map((p) => (
            <option key={p.id} value={p.id}>
              {p.brand_name} {p.name}
            </option>
          ))}
        </select>
        <input required value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" className="w-full rounded-lg border px-3 py-2" />
        <textarea required value={body} onChange={(e) => setBody(e.target.value)} rows={6} className="w-full rounded-lg border px-3 py-2" />
        <select value={rating} onChange={(e) => setRating(e.target.value)} className="rounded-lg border px-3 py-2">
          {[1, 2, 3, 4, 5].map((n) => (
            <option key={n} value={n}>
              {n} stars
            </option>
          ))}
        </select>
        <button type="submit" className="rounded-full bg-teal-700 px-4 py-2 text-white">
          Save draft
        </button>
      </form>
    </div>
  );
}

export default function NewReviewPage() {
  return (
    <Suspense fallback={<p>Loading…</p>}>
      <Form />
    </Suspense>
  );
}
