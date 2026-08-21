"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ReviewCard, type ReviewItem } from "@/components/ReviewCard";
import { api } from "@/lib/api";

type Profile = {
  username: string;
  display_name: string | null;
  biography: string | null;
  interests: string[];
  reviews: ReviewItem[];
};

export default function PublicProfilePage() {
  const { username } = useParams<{ username: string }>();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Profile>(`/api/v1/users/${username}`)
      .then(setProfile)
      .catch((err) => setError(err instanceof Error ? err.message : "Profile not found."));
  }, [username]);

  if (error) return <p className="text-red-400">{error}</p>;
  if (!profile) return <p className="muted">Loading…</p>;

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="feed-kicker">Public profile</p>
        <h1 className="text-3xl font-bold">@{profile.username}</h1>
        {profile.display_name ? <p>{profile.display_name}</p> : null}
        {profile.biography ? <p className="muted">{profile.biography}</p> : null}
        {profile.interests.length ? <p className="muted text-sm">Interests: {profile.interests.join(", ")}</p> : null}
      </header>
      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Published reviews</h2>
        {profile.reviews.length ? (
          profile.reviews.map((review) => <ReviewCard key={review.id} review={review} variant="compact" />)
        ) : (
          <p className="muted">No published reviews yet.</p>
        )}
      </section>
    </div>
  );
}
