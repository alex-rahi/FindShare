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
  if (!product) return <p className="muted">Loading…</p>;
  return (
    <article className="space-y-6">
      <p className="feed-kicker">
        {product.category.name} · {product.brand_name}
      </p>
      <h1 className="text-4xl font-bold">{product.name}</h1>
      <p className="muted">{product.description}</p>
      <Link href={`/reviews/new?product=${product.id}`} className="btn inline-block">
        Write a review
      </Link>
      {product.category.requires_health_notice ? <p className="notice">{NOTICES.health}</p> : null}
      <div className="space-y-3">
        {reviews.map((review) => (
          <ReviewCard key={review.id} review={review} variant="compact" />
        ))}
      </div>
    </article>
  );
}
