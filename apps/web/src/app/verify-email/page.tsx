"use client";

import { FormEvent, useState } from "react";
import { api } from "@/lib/api";

export default function VerifyPage() {
  const [token, setToken] = useState("");
  const [done, setDone] = useState(false);
  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    await api("/api/v1/auth/verify-email", { method: "POST", body: JSON.stringify({ token }) });
    setDone(true);
  }
  return (
    <div className="mx-auto max-w-md space-y-4">
      <h1 className="serif text-3xl">Verify email</h1>
      {done ? (
        <p>Email verified.</p>
      ) : (
        <form onSubmit={onSubmit} className="space-y-3 rounded-2xl border bg-white p-6">
          <input required value={token} onChange={(e) => setToken(e.target.value)} placeholder="Token" className="w-full rounded-lg border px-3 py-2" />
          <button type="submit" className="w-full rounded-full bg-teal-700 py-2 text-white">
            Verify
          </button>
        </form>
      )}
    </div>
  );
}
