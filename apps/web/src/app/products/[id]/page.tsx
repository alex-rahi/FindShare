"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ReviewCard, type ReviewItem } from "@/components/ReviewCard";
import { NOTICES } from "@/components/Footer";
import { api } from "@/lib/api";

type Product = {
  id: string;
  name: string;
  description: string | null;
  brand_name: string;
  category: { name: string; requires_health_notice: boolean };
  average_rating: number | null;
  review_count: number;
};

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  useEffect(() => {
    api<Product>(`/api/v1/products/${id}`).then(setProduct);
    api<{ items: ReviewItem[] }>(`/api/v1/reviews?product_id=${id}`).then((body) => setReviews(body.items));
  }, [id]);
  if (!product) return <p>Loading…</p>;
  return (
    <article className="space-y-6">
      <p className="text-xs uppercase text-orange-700">
        {product.category.name} · {product.brand_name}
      </p>
      <h1 className="serif text-4xl">{product.name}</h1>
      <p className="text-slate-600">{product.description}</p>
      <Link href={`/reviews/new?product=${product.id}`} className="underline">
        Write a review
      </Link>
      {product.category.requires_health_notice ? <p className="rounded-xl bg-orange-50 p-4 text-sm">{NOTICES.health}</p> : null}
      <div className="grid gap-4 sm:grid-cols-2">
        {reviews.map((review) => (
          <ReviewCard key={review.id} review={review} />
        ))}
      </div>
    </article>
  );
}
