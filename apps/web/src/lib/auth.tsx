"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api, setToken } from "./api";

type SessionUser = { id: string; email: string; username: string; role: string };

const AuthContext = createContext<{
  user: SessionUser | null;
  ready: boolean;
  login: (emailOrUsername: string, password: string) => Promise<void>;
  register: (payload: {
    email: string;
    username: string;
    password: string;
    invitation_code?: string;
  }) => Promise<{ local_verify_token?: string | null }>;
  logout: () => Promise<void>;
} | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    api<{ user: SessionUser }>("/api/v1/auth/me")
      .then((body) => setUser(body.user))
      .catch(() => setUser(null))
      .finally(() => setReady(true));
  }, []);

  const value = useMemo(
    () => ({
      user,
      ready,
      async login(emailOrUsername: string, password: string) {
        const body = await api<{ user: SessionUser; tokens: { access_token: string } }>("/api/v1/auth/login", {
          method: "POST",
          body: JSON.stringify({ email_or_username: emailOrUsername, password }),
        });
        setToken(body.tokens.access_token);
        setUser(body.user);
      },
      async register(payload: {
        email: string;
        username: string;
        password: string;
        invitation_code?: string;
      }) {
        const body = await api<{
          user: SessionUser;
          tokens: { access_token: string };
          local_verify_token?: string | null;
        }>("/api/v1/auth/register", { method: "POST", body: JSON.stringify(payload) });
        setToken(body.tokens.access_token);
        setUser(body.user);
        return { local_verify_token: body.local_verify_token };
      },
      async logout() {
        try {
          await api("/api/v1/auth/logout", { method: "POST" });
        } finally {
          setToken(null);
          setUser(null);
        }
      },
    }),
    [user, ready],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
