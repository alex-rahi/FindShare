"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Product = { id: string; name: string; brand_name: string; category: { name: string }; average_rating: number | null };

export default function ProductsPage() {
  const [items, setItems] = useState<Product[]>([]);
  useEffect(() => {
    api<{ items: Product[] }>("/api/v1/products").then((body) => setItems(body.items));
  }, []);
  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <h1 className="serif text-3xl">Products</h1>
        <Link href="/products/new" className="rounded-full bg-teal-700 px-4 py-2 text-sm text-white">
          Add product
        </Link>
      </div>
      <ul className="divide-y rounded-2xl border bg-white">
        {items.map((product) => (
          <li key={product.id} className="px-4 py-3">
            <Link href={`/products/${product.id}`}>
              {product.brand_name} {product.name}
              <span className="block text-sm text-slate-500">{product.category.name}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
