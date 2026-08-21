"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

type BetaStatus = {
  registration_mode: string;
  registration_enabled: boolean;
  seats_remaining: number;
  maximum_active_users: number;
  maintenance_mode: boolean;
};

export default function RegisterPage() {
  const { register } = useAuth();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [invitation, setInvitation] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [beta, setBeta] = useState<BetaStatus | null>(null);

  useEffect(() => {
    api<BetaStatus>("/api/v1/beta/status").then(setBeta).catch(() => setBeta(null));
  }, []);

  const inviteOnly = beta?.registration_mode === "invite_only";
  const closed =
    beta && (!beta.registration_enabled || beta.maintenance_mode || (inviteOnly && beta.seats_remaining <= 0));

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      const result = await register({
        email,
        username,
        password,
        invitation_code: invitation || undefined,
      });
      setToken(result.local_verify_token ?? null);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Registration failed.");
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Create an account</h1>
      {closed ? (
        <p className="notice">
          FindShare is in a closed invitation-only beta
          {beta && inviteOnly ? ` (${beta.maximum_active_users} active testers maximum)` : ""}. There are no seats
          remaining, or registration is paused. Ask an administrator for a waitlist invitation.
        </p>
      ) : null}
      {token ? (
        <p className="panel break-all text-sm">
          Account created. Local verification token (development only): {token}.{" "}
          <Link href={`/verify-email?token=${encodeURIComponent(token)}`}>Verify email</Link>
        </p>
      ) : (
        <form onSubmit={onSubmit} className="panel">
          {error ? <p className="text-sm text-red-400">{error}</p> : null}
          {inviteOnly ? (
            <p className="muted text-sm">
              Invitation-only beta. Use the local seed code <code>FINDSHARE-DEV-INVITE</code> in development.
            </p>
          ) : null}
          <input required type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="field" />
          <input required minLength={3} placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} className="field" />
          <input required type="password" minLength={10} placeholder="Password (10+ with upper, lower, digit, symbol)" value={password} onChange={(e) => setPassword(e.target.value)} className="field" />
          <input
            required={inviteOnly}
            placeholder="Invitation code"
            value={invitation}
            onChange={(e) => setInvitation(e.target.value)}
            className="field"
          />
          <button type="submit" className="btn" disabled={Boolean(closed)}>
            Join FindShare
          </button>
        </form>
      )}
      <p className="muted">
        Already have an account? <Link href="/login">Sign in</Link>
      </p>
    </div>
  );
}
