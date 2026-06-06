"use client";

import { useEffect, useState } from "react";

import { cn } from "@/lib/utils";

import { Section } from "../../ui/section";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Product {
  name: string;
  category: string;
  avg_rating: number;
  review_count: number;
  bayesian_score: number;
  rank_change?: number;
}

interface RecoData {
  fake_count: number;
  genuine_count: number;
  total_reviews: number;
  with_fake: Product[];
  without_fake: Product[];
}

function Table({ products, showRankChange }: { products: Product[]; showRankChange?: boolean }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-border border-b">
            <th className="text-muted-foreground px-3 py-2 text-left text-[10px] font-bold tracking-widest uppercase">#</th>
            <th className="text-muted-foreground px-3 py-2 text-left text-[10px] font-bold tracking-widest uppercase">Product</th>
            <th className="text-muted-foreground px-3 py-2 text-right text-[10px] font-bold tracking-widest uppercase">Rating</th>
            <th className="text-muted-foreground px-3 py-2 text-right text-[10px] font-bold tracking-widest uppercase">Reviews</th>
            <th className="text-muted-foreground px-3 py-2 text-right text-[10px] font-bold tracking-widest uppercase">Score</th>
            {showRankChange && <th className="text-muted-foreground px-3 py-2 text-right text-[10px] font-bold tracking-widest uppercase">Change</th>}
          </tr>
        </thead>
        <tbody>
          {products.map((p, i) => (
            <tr key={p.name} className="border-border border-b last:border-0">
              <td className="text-muted-foreground px-3 py-3">{i + 1}</td>
              <td className="px-3 py-3">
                <div className="font-semibold">{p.name}</div>
                <div className="text-muted-foreground text-xs">{p.category}</div>
              </td>
              <td className="px-3 py-3 text-right">{p.avg_rating.toFixed(2)}★</td>
              <td className="text-muted-foreground px-3 py-3 text-right">{p.review_count}</td>
              <td className="text-brand px-3 py-3 text-right font-mono font-bold">{p.bayesian_score.toFixed(3)}</td>
              {showRankChange && (
                <td className={cn("px-3 py-3 text-right font-bold", (p.rank_change ?? 0) > 0 ? "text-green-400" : (p.rank_change ?? 0) < 0 ? "text-red-400" : "text-muted-foreground")}>
                  {(p.rank_change ?? 0) > 0 ? `▲ +${p.rank_change}` : (p.rank_change ?? 0) < 0 ? `▼ ${p.rank_change}` : "—"}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function RecommendationsSection({ className }: { className?: string }) {
  const [data, setData] = useState<RecoData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API}/api/recommendations`)
      .then(r => r.json())
      .then(setData)
      .catch(e => setError(String(e)));
  }, []);

  return (
    <Section id="recommendations" className={cn(className)}>
      <div className="max-w-container mx-auto flex flex-col gap-12">
        <div className="flex flex-col items-center gap-4 text-center">
          <span className="text-brand text-xs font-bold tracking-widest uppercase">Recommendation System</span>
          <h2 className="text-3xl leading-tight font-semibold sm:text-5xl">How Fake Reviews Distort Rankings</h2>
          <p className="text-muted-foreground max-w-[600px] font-medium">
            Fake reviews inflate ratings for certain products, pushing them unfairly to the top. Filtering them restores honest rankings.
          </p>
        </div>

        {error && <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">Could not load data: {error}</div>}

        {data && (
          <>
            <div className="border-brand/30 bg-brand/5 rounded-lg border p-4 text-center text-sm">
              Dataset: <strong>{data.total_reviews} reviews</strong> — {data.genuine_count} genuine + <strong>{data.fake_count} fake</strong> ({((data.fake_count / data.total_reviews) * 100).toFixed(0)}% injection rate)
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <div className="bg-card border-border rounded-2xl border">
                <div className="border-border border-b p-4">
                  <h3 className="font-semibold">Before Filtering</h3>
                  <p className="text-muted-foreground text-xs">Rankings include fake reviews</p>
                </div>
                <Table products={data.with_fake} />
              </div>
              <div className="bg-card border-border rounded-2xl border">
                <div className="border-border border-b p-4">
                  <h3 className="font-semibold">After Filtering</h3>
                  <p className="text-muted-foreground text-xs">Fake reviews removed</p>
                </div>
                <Table products={data.without_fake} showRankChange />
              </div>
            </div>
          </>
        )}

        {!data && !error && (
          <div className="text-muted-foreground text-center text-sm">Loading recommendations...</div>
        )}
      </div>
    </Section>
  );
}
