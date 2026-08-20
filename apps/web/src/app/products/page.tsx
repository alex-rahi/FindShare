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
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Shop</h1>
        <Link href="/products/new" className="btn">
          Add product
        </Link>
      </div>
      <ul className="space-y-3">
        {items.map((product) => (
          <li key={product.id}>
            <Link href={`/products/${product.id}`} className="compact-card">
              {product.brand_name} {product.name}
              <span className="muted block text-sm">{product.category.name}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
