"use client";

import { FormEvent, useState } from "react";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const { register } = useAuth();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [invitation, setInvitation] = useState("FINDSHARE-DEV-INVITE");
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      const result = await register({
        email,
        username,
        password,
        invitation_code: invitation,
      });
      setToken(result.local_verify_token ?? null);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Registration failed.");
    }
  }

  return (
    <div className="mx-auto max-w-md space-y-6">
      <h1 className="serif text-3xl">Invitation-only access</h1>
      {token ? (
        <p className="break-all rounded-2xl border border-slate-200 bg-white p-6 text-sm">
          Account created. Local verification token: {token}. Visit /verify-email.
        </p>
      ) : (
        <form onSubmit={onSubmit} className="space-y-3 rounded-2xl border border-slate-200 bg-white p-6">
          {error ? <p className="text-sm text-red-700">{error}</p> : null}
          <input required type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
          <input required minLength={3} placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
          <input required type="password" minLength={10} placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
          <input required placeholder="Invitation code" value={invitation} onChange={(e) => setInvitation(e.target.value)} className="w-full rounded-lg border px-3 py-2" />
          <button type="submit" className="w-full rounded-full bg-teal-700 py-2 text-white">
            Create account
          </button>
        </form>
      )}
    </div>
  );
}
