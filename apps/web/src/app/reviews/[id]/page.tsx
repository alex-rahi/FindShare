"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { NOTICES } from "@/components/Footer";

type Review = {
  id: string;
  title: string;
  body: string;
  overall_rating: number;
  state: string;
  review_kind: string;
  recommended: boolean | null;
  author: { id: string; username: string };
  product: { id: string; name: string; brand_name: string; category: { requires_health_notice: boolean } };
};

export default function ReviewPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const router = useRouter();
  const [review, setReview] = useState<Review | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    api<Review>(`/api/v1/reviews/${id}`)
      .then(setReview)
      .catch((err) => setError(err.message));
  }, [id]);
  if (error) return <p className="text-red-700">{error}</p>;
  if (!review) return <p>Loading…</p>;
  const mine = user?.id === review.author.id;
  return (
    <article className="space-y-4">
      <p className="text-xs uppercase text-orange-700">
        {review.state} · {review.review_kind} · {review.overall_rating}/5
      </p>
      <h1 className="serif text-4xl">{review.title}</h1>
      <p>
        <Link href={`/products/${review.product.id}`} className="underline">
          {review.product.brand_name} {review.product.name}
        </Link>{" "}
        · @{review.author.username}
      </p>
      {mine && review.state !== "published" ? (
        <button
          type="button"
          className="underline"
          onClick={async () => {
            setReview(await api<Review>(`/api/v1/reviews/${id}/publish`, { method: "POST" }));
          }}
        >
          Publish (local shortcut)
        </button>
      ) : null}
      {mine ? (
        <button
          type="button"
          className="ml-3 underline"
          onClick={async () => {
            await api(`/api/v1/reviews/${id}`, { method: "DELETE" });
            router.push("/");
          }}
        >
          Delete
        </button>
      ) : null}
      <p className="whitespace-pre-wrap leading-relaxed">{review.body}</p>
      {review.product.category.requires_health_notice ? <p className="rounded-xl bg-orange-50 p-4 text-sm">{NOTICES.health}</p> : null}
    </article>
  );
}
