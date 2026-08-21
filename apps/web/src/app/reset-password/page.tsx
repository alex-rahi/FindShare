"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { ApiError, api } from "@/lib/api";

export default function ResetPasswordPage() {
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [localToken, setLocalToken] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function requestReset(event: FormEvent) {
    event.preventDefault();
    try {
      const body = await api<{ local_reset_token?: string | null }>("/api/v1/auth/password-reset/request", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      setLocalToken(body.local_reset_token ?? null);
      if (body.local_reset_token) setToken(body.local_reset_token);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not request a reset.");
    }
  }

  async function confirmReset(event: FormEvent) {
    event.preventDefault();
    try {
      await api("/api/v1/auth/password-reset/confirm", {
        method: "POST",
        body: JSON.stringify({ token, new_password: password }),
      });
      setDone(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not reset password.");
    }
  }

  if (done) {
    return (
      <div className="space-y-4">
        <h1 className="text-3xl font-bold">Password updated</h1>
        <p>
          You can <Link href="/login">sign in</Link> with the new password.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Reset password</h1>
      <form onSubmit={requestReset} className="panel">
        {error ? <p className="text-sm text-red-400">{error}</p> : null}
        <input required type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" className="field" />
        <button type="submit" className="btn">
          Request reset
        </button>
        {localToken ? (
          <p className="muted break-all text-sm">Local development token: {localToken}</p>
        ) : null}
      </form>
      <form onSubmit={confirmReset} className="panel">
        <input required value={token} onChange={(e) => setToken(e.target.value)} placeholder="Reset token" className="field" />
        <input required type="password" minLength={10} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="New password" className="field" />
        <button type="submit" className="btn">
          Set new password
        </button>
      </form>
    </div>
  );
}
