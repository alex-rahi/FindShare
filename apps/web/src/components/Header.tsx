"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth";

export function Header() {
  const { user, logout, ready } = useAuth();
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
        <Link href="/" className="serif text-2xl font-semibold text-teal-700">
          FindShare
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link href="/" className="hover:underline">
            Feed
          </Link>
          <Link href="/products" className="hover:underline">
            Products
          </Link>
          {ready && user ? (
            <>
              <Link href="/reviews/new" className="hover:underline">
                Write review
              </Link>
              <Link href="/me" className="hover:underline">
                @{user.username}
              </Link>
              <button type="button" onClick={() => void logout()} className="hover:underline">
                Sign out
              </button>
            </>
          ) : ready ? (
            <>
              <Link href="/login" className="hover:underline">
                Sign in
              </Link>
              <Link href="/register" className="rounded-full bg-teal-700 px-3 py-1 text-white">
                Join
              </Link>
            </>
          ) : null}
        </nav>
      </div>
    </header>
  );
}
