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
  const [description, setDescription] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [subcategoryId, setSubcategoryId] = useState("");
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

  const selected = categories.find((c) => c.id === categoryId);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      const product = await api<{ id: string }>("/api/v1/products", {
        method: "POST",
        body: JSON.stringify({
          name,
          brand_name: brand,
          description: description || null,
          category_id: categoryId,
          subcategory_id: subcategoryId || null,
        }),
      });
      router.push(`/products/${product.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create product.");
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Add a product</h1>
      <p className="muted text-sm">Categories and subcategories are loaded from the API, not hardcoded.</p>
      <form onSubmit={onSubmit} className="panel">
        {error ? <p className="text-sm text-red-400">{error}</p> : null}
        <input required value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" className="field" />
        <input required value={brand} onChange={(e) => setBrand(e.target.value)} placeholder="Brand" className="field" />
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" className="field" />
        <select
          value={categoryId}
          onChange={(e) => {
            setCategoryId(e.target.value);
            setSubcategoryId("");
          }}
          className="field"
        >
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <select value={subcategoryId} onChange={(e) => setSubcategoryId(e.target.value)} className="field">
          <option value="">No subcategory</option>
          {(selected?.subcategories ?? []).map((sub) => (
            <option key={sub.id} value={sub.id}>
              {sub.name}
            </option>
          ))}
        </select>
        <button type="submit" className="btn">
          Save
        </button>
      </form>
    </div>
  );
}
