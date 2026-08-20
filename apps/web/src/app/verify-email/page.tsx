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
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Verify email</h1>
      {done ? (
        <p>Email verified.</p>
      ) : (
        <form onSubmit={onSubmit} className="panel">
          <input required value={token} onChange={(e) => setToken(e.target.value)} placeholder="Token" className="field" />
          <button type="submit" className="btn">
            Verify
          </button>
        </form>
      )}
    </div>
  );
}
