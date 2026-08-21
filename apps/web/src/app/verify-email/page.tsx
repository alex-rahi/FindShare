"use client";

import { FormEvent, Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

function VerifyForm() {
  const search = useSearchParams();
  const [token, setToken] = useState(search.get("token") ?? "");
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      await api("/api/v1/auth/verify-email", { method: "POST", body: JSON.stringify({ token }) });
      setDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Verification failed.");
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Verify email</h1>
      {done ? (
        <p>
          Email verified. You can <Link href="/login">sign in</Link> and publish reviews.
        </p>
      ) : (
        <form onSubmit={onSubmit} className="panel">
          {error ? <p className="text-sm text-red-400">{error}</p> : null}
          <input required value={token} onChange={(e) => setToken(e.target.value)} placeholder="Token" className="field" />
          <button type="submit" className="btn">
            Verify
          </button>
        </form>
      )}
    </div>
  );
}

export default function VerifyPage() {
  return (
    <Suspense fallback={<p className="muted">Loading…</p>}>
      <VerifyForm />
    </Suspense>
  );
}
