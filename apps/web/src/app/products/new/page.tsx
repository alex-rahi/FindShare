"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

type Category = { id: string; name: string; slug: string; subcategories: { id: string; slug: string; name: string }[] };

export default function NewProductPage() {
  const { user, ready } = useAuth();
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [name, setName] = useState("");
  const [brand, setBrand] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (ready && !user) router.push("/login");
  }, [ready, user, router]);
  useEffect(() => {
    api<Category[]>("/api/v1/categories").then((items) => {
      setCategories(items);
      if (items[0]) setCategoryId(items[0].id);
    });
  }, []);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      const product = await api<{ id: string }>("/api/v1/products", {
        method: "POST",
        body: JSON.stringify({ name, brand_name: brand, category_id: categoryId }),
      });
      router.push(`/products/${product.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create product.");
    }
  }

  return (
    <div className="mx-auto max-w-lg space-y-4">
      <h1 className="serif text-3xl">Add a product</h1>
      <form onSubmit={onSubmit} className="space-y-3 rounded-2xl border bg-white p-6">
        {error ? <p className="text-sm text-red-700">{error}</p> : null}
        <input required value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" className="w-full rounded-lg border px-3 py-2" />
        <input required value={brand} onChange={(e) => setBrand(e.target.value)} placeholder="Brand" className="w-full rounded-lg border px-3 py-2" />
        <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} className="w-full rounded-lg border px-3 py-2">
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <button type="submit" className="rounded-full bg-teal-700 px-4 py-2 text-white">
          Save
        </button>
      </form>
    </div>
  );
}
