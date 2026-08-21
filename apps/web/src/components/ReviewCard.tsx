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

export function ReviewCard({
  review,
  variant = "feed",
}: {
  review: ReviewItem;
  variant?: "feed" | "compact";
}) {
  const initial = review.author.username.slice(0, 1).toUpperCase();

  if (variant === "compact") {
    return (
      <Link href={`/reviews/${review.id}`} className="compact-card">
        <p className="feed-kicker">
          {review.product.category.name} · {review.product.brand_name}
        </p>
        <h2>{review.title}</h2>
        <p className="muted">
          {review.overall_rating}/5 · @{review.author.username}
        </p>
      </Link>
    );
  }

  return (
    <article className="feed-card">
      <div className="feed-stage" aria-hidden>
        <p>{review.product.brand_name}</p>
        <p className="feed-stage-name">{review.product.name}</p>
      </div>
      <div className="feed-gradient" />
      <div className="feed-caption">
        <p className="feed-kicker">
          {review.product.category.name} · {review.product.brand_name}
        </p>
        <Link href={`/reviews/${review.id}`} className="feed-title">
          {review.title}
        </Link>
        <p className="feed-body">{review.body}</p>
        <p className="feed-author">
          <Link href={`/users/${review.author.username}`}>@{review.author.username}</Link>
        </p>
      </div>
      <aside className="feed-rail">
        <div className="feed-avatar">{initial}</div>
        <div className="feed-action">
          <span aria-hidden>★</span>
          <span>{review.overall_rating}</span>
        </div>
        <Link href={`/reviews/${review.id}`} className="feed-action">
          <span aria-hidden>▸</span>
          <span>Open</span>
        </Link>
      </aside>
    </article>
  );
}
