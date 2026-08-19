import type { Metadata } from "next";

export const metadata: Metadata = { title: "FindShare Admin" };

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
