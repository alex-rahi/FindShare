"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function MePage() {
  const { user, ready, logout } = useAuth();
  const router = useRouter();
  const [biography, setBiography] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [interests, setInterests] = useState("");

  useEffect(() => {
    if (ready && !user) router.push("/login");
  }, [ready, user, router]);

  useEffect(() => {
    if (!user) return;
    api<{ profile: { biography: string | null; display_name: string | null; interests: string[] } }>("/api/v1/auth/me").then(
      (body) => {
        setBiography(body.profile?.biography ?? "");
        setDisplayName(body.profile?.display_name ?? "");
        setInterests((body.profile?.interests ?? []).join(", "));
      },
    );
  }, [user]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    await api("/api/v1/profiles/me", {
      method: "PATCH",
      body: JSON.stringify({
        display_name: displayName,
        biography,
        interests: interests.split(",").map((s) => s.trim()).filter(Boolean),
      }),
    });
  }

  if (!user) return <p className="muted">Loading…</p>;
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">You</h1>
      <form onSubmit={onSubmit} className="panel">
        <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} className="field" placeholder="Display name" />
        <textarea value={biography} onChange={(e) => setBiography(e.target.value)} className="field" placeholder="Bio" />
        <input value={interests} onChange={(e) => setInterests(e.target.value)} placeholder="Interests" className="field" />
        <button type="submit" className="btn">
          Save
        </button>
      </form>
      <button
        type="button"
        className="text-sm text-red-400 underline"
        onClick={async () => {
          await api("/api/v1/users/me", { method: "DELETE" });
          await logout();
          router.push("/");
        }}
      >
        Delete account
      </button>
    </div>
  );
}
