"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [ident, setIdent] = useState("admin");
  const [password, setPassword] = useState("FindShareAdmin!dev");
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
    <div className="mx-auto max-w-md space-y-6">
      <h1 className="serif text-3xl">Sign in</h1>
      <form onSubmit={onSubmit} className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6">
        {error ? <p className="text-sm text-red-700">{error}</p> : null}
        <input
          value={ident}
          onChange={(e) => setIdent(e.target.value)}
          placeholder="Email or username"
          className="w-full rounded-lg border border-slate-200 px-3 py-2"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded-lg border border-slate-200 px-3 py-2"
        />
        <button type="submit" className="w-full rounded-full bg-teal-700 py-2 text-white">
          Sign in
        </button>
      </form>
    </div>
  );
}
