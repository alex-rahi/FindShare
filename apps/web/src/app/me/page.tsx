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

  if (!user) return <p>Loading…</p>;
  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="serif text-3xl">Your profile</h1>
      <form onSubmit={onSubmit} className="space-y-3 rounded-2xl border bg-white p-6">
        <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
        <textarea value={biography} onChange={(e) => setBiography(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
        <input value={interests} onChange={(e) => setInterests(e.target.value)} placeholder="Interests" className="w-full rounded-lg border px-3 py-2" />
        <button type="submit" className="rounded-full bg-teal-700 px-4 py-2 text-white">
          Save
        </button>
      </form>
      <button
        type="button"
        className="text-sm text-red-700 underline"
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
