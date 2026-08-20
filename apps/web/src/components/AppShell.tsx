"use client";

import Link from "next/link";
import { Suspense } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { TabBar } from "@/components/TabBar";
import { useAuth } from "@/lib/auth";

function FeedChrome() {
  const search = useSearchParams();
  const { user, logout, ready } = useAuth();
  const recent = search.get("sort") === "recent";

  return (
    <header className="feed-top">
      <span className="feed-brand">FindShare</span>
      <span className="feed-top-tabs">
        <Link href="/" className={recent ? "" : "is-on"}>
          For you
        </Link>
        <Link href="/?sort=recent" className={recent ? "is-on" : ""}>
          Recent
        </Link>
      </span>
      {ready && user ? (
        <button type="button" className="feed-ghost" onClick={() => void logout()}>
          Sign out
        </button>
      ) : (
        <Link href="/login" className="feed-ghost">
          Sign in
        </Link>
      )}
    </header>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, ready } = useAuth();
  const isFeed = pathname === "/";

  return (
    <>
      {isFeed ? (
        <Suspense>
          <FeedChrome />
        </Suspense>
      ) : (
        <header className="page-top">
          <Link href="/" className="feed-brand">
            FindShare
          </Link>
          {ready && user ? <span className="muted">@{user.username}</span> : <Link href="/register">Join</Link>}
        </header>
      )}
      <div className={isFeed ? "feed-root" : "page-root"}>{children}</div>
      <TabBar />
    </>
  );
}
