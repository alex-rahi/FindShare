"use client";

import { FormEvent, useState } from "react";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const { register } = useAuth();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      const result = await register({ email, username, password });
      setToken(result.local_verify_token ?? null);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Registration failed.");
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Create an account</h1>
      {token ? (
        <p className="panel break-all text-sm">
          Account created. Local verification token: {token}. Visit /verify-email.
        </p>
      ) : (
        <form onSubmit={onSubmit} className="panel">
          {error ? <p className="text-sm text-red-400">{error}</p> : null}
          <input required type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="field" />
          <input required minLength={3} placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} className="field" />
          <input required type="password" minLength={10} placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="field" />
          <button type="submit" className="btn">
            Join FindShare
          </button>
        </form>
      )}
    </div>
  );
}
