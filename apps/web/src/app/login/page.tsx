"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [ident, setIdent] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      await login(ident, password);
      router.push("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Sign in failed.");
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Sign in</h1>
      <p className="muted text-sm">
        Seeded local accounts are demonstration data. Registration is invitation-only by default.
      </p>
      <form onSubmit={onSubmit} className="panel">
        {error ? <p className="text-sm text-red-400">{error}</p> : null}
        <input
          value={ident}
          onChange={(e) => setIdent(e.target.value)}
          placeholder="Email or username"
          className="field"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          className="field"
        />
        <button type="submit" className="btn">
          Sign in
        </button>
      </form>
      <p className="muted">
        New here? <Link href="/register">Create an account</Link>
      </p>
      <p className="muted">
        <Link href="/reset-password">Forgot password?</Link>
      </p>
    </div>
  );
}
