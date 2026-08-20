"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";

const TABS = [
  { href: "/", label: "Feed", icon: "⌂" },
  { href: "/products", label: "Shop", icon: "▣" },
  { href: "/reviews/new", label: "Post", icon: "+" },
  { href: "/me", label: "You", icon: "●" },
];

export function TabBar() {
  const pathname = usePathname();
  const { user, ready } = useAuth();

  return (
    <nav className="tab-bar">
      {TABS.map((tab) => {
        const href = tab.href === "/me" && ready && !user ? "/login" : tab.href;
        const active = pathname === tab.href || (tab.href !== "/" && pathname.startsWith(tab.href));
        return (
          <Link key={tab.href} href={href} className={active ? "tab-item tab-item-active" : "tab-item"}>
            <span className={tab.label === "Post" ? "tab-post" : ""}>{tab.icon}</span>
            <span>{tab.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
