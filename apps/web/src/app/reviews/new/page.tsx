"use client";

import { FormEvent, Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

const KINDS = [
  { value: "personal", label: "Personal review" },
  { value: "recommendation", label: "Product recommendation" },
  { value: "first_impression", label: "First impression" },
  { value: "long_term", label: "Long-term review" },
  { value: "comparison", label: "Comparison review" },
  { value: "question", label: "Question or discussion" },
];

function Form() {
  const { user, ready } = useAuth();
  const router = useRouter();
  const search = useSearchParams();
  const [products, setProducts] = useState<{ id: string; name: string; brand_name: string }[]>([]);
  const [productId, setProductId] = useState(search.get("product") ?? "");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [rating, setRating] = useState("5");
  const [pros, setPros] = useState("");
  const [cons, setCons] = useState("");
  const [kind, setKind] = useState("personal");
  const [recommended, setRecommended] = useState("yes");
  const [publish, setPublish] = useState(false);
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
          pros: pros.split("\n").map((s) => s.trim()).filter(Boolean),
          cons: cons.split("\n").map((s) => s.trim()).filter(Boolean),
          recommended: recommended === "yes",
          review_kind: kind,
          publish,
        }),
      });
      router.push(`/reviews/${review.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save.");
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Write a review</h1>
      <p className="muted text-sm">Text-only in Phase 1. Image uploads are disabled.</p>
      <form onSubmit={onSubmit} className="panel">
        {error ? <p className="text-sm text-red-400">{error}</p> : null}
        <select required value={productId} onChange={(e) => setProductId(e.target.value)} className="field">
          <option value="">Select product</option>
          {products.map((p) => (
            <option key={p.id} value={p.id}>
              {p.brand_name} {p.name}
            </option>
          ))}
        </select>
        <input required value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" className="field" />
        <textarea required value={body} onChange={(e) => setBody(e.target.value)} rows={6} placeholder="Written review" className="field" />
        <select value={rating} onChange={(e) => setRating(e.target.value)} className="field">
          {[1, 2, 3, 4, 5].map((n) => (
            <option key={n} value={n}>
              {n} stars
            </option>
          ))}
        </select>
        <select value={kind} onChange={(e) => setKind(e.target.value)} className="field">
          {KINDS.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
        <select value={recommended} onChange={(e) => setRecommended(e.target.value)} className="field">
          <option value="yes">Recommended</option>
          <option value="no">Not recommended</option>
        </select>
        <textarea value={pros} onChange={(e) => setPros(e.target.value)} placeholder="Pros (one per line)" className="field" />
        <textarea value={cons} onChange={(e) => setCons(e.target.value)} placeholder="Cons (one per line)" className="field" />
        <label className="muted text-sm">
          <input type="checkbox" checked={publish} onChange={(e) => setPublish(e.target.checked)} /> Publish immediately
        </label>
        <button type="submit" className="btn">
          {publish ? "Publish review" : "Save draft"}
        </button>
      </form>
    </div>
  );
}

export default function NewReviewPage() {
  return (
    <Suspense fallback={<p className="muted">Loading…</p>}>
      <Form />
    </Suspense>
  );
}
