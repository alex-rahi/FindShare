import Link from "next/link";

export type ReviewItem = {
  id: string;
  title: string;
  body: string;
  overall_rating: number;
  state: string;
  author: { username: string };
  product: { name: string; brand_name: string; category: { name: string } };
};

export function ReviewCard({ review }: { review: ReviewItem }) {
  return (
    <Link href={`/reviews/${review.id}`} className="block rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-xs uppercase tracking-wide text-orange-700">
        {review.product.category.name} · {review.product.brand_name}
      </p>
      <h2 className="serif mt-1 text-xl">{review.title}</h2>
      <p className="text-sm text-orange-700" aria-label={`${review.overall_rating} out of 5`}>
        {"★".repeat(review.overall_rating)}
        {"☆".repeat(5 - review.overall_rating)}
      </p>
      <p className="mt-2 line-clamp-2 text-sm text-slate-600">{review.body}</p>
      <p className="mt-2 text-xs text-slate-500">
        {review.product.name} · @{review.author.username}
      </p>
    </Link>
  );
}
