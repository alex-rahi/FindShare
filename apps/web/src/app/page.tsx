"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ReviewCard, type ReviewItem } from "@/components/ReviewCard";
import { api } from "@/lib/api";

function Feed() {
  const search = useSearchParams();
  const sort = search.get("sort") === "recent" ? "recent" : "popular";
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setItems([]);
    setError(null);
    api<{ items: ReviewItem[] }>(`/api/v1/feed?sort=${sort}`)
      .then((data) => setItems(data.items))
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load feed."));
  }, [sort]);

  if (error) {
    return <p className="feed-status">{error}</p>;
  }
  if (!items.length) {
    return <p className="feed-status">No published reviews yet.</p>;
  }

  return (
    <div className="feed-stack">
      {items.map((review) => (
        <ReviewCard key={review.id} review={review} />
      ))}
    </div>
  );
}

export default function HomePage() {
  return (
    <Suspense fallback={<p className="feed-status">Loading feed…</p>}>
      <Feed />
    </Suspense>
  );
}
