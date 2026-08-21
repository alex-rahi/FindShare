"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { api } from "@/lib/api";

type Category = { id: string; slug: string; name: string };
type Product = {
  id: string;
  name: string;
  brand_name: string;
  category: { name: string; slug: string };
  average_rating: number | null;
};

export default function ProductsPage() {
  const [items, setItems] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [q, setQ] = useState("");
  const [category, setCategory] = useState("");

  function load(nextQ = q, nextCategory = category) {
    const params = new URLSearchParams();
    if (nextQ.trim()) params.set("q", nextQ.trim());
    if (nextCategory) params.set("category", nextCategory);
    api<{ items: Product[] }>(`/api/v1/products?${params.toString()}`).then((body) => setItems(body.items));
  }

  useEffect(() => {
    api<Category[]>("/api/v1/categories").then(setCategories);
    load("", "");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    load();
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Shop</h1>
        <Link href="/products/new" className="btn">
          Add product
        </Link>
      </div>
      <form onSubmit={onSubmit} className="panel">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search products or brands" className="field" />
        <select
          value={category}
          onChange={(e) => {
            setCategory(e.target.value);
            load(q, e.target.value);
          }}
          className="field"
        >
          <option value="">All categories</option>
          {categories.map((item) => (
            <option key={item.id} value={item.slug}>
              {item.name}
            </option>
          ))}
        </select>
        <button type="submit" className="btn">
          Filter
        </button>
      </form>
      <ul className="space-y-3">
        {items.map((product) => (
          <li key={product.id}>
            <Link href={`/products/${product.id}`} className="compact-card">
              {product.brand_name} {product.name}
              <span className="muted block text-sm">
                {product.category.name}
                {product.average_rating ? ` · ${product.average_rating}/5` : ""}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
