"use client";

import { useEffect, useState } from "react";

import { cn } from "@/lib/utils";

import { Section } from "../../ui/section";

const API = "http://localhost:8000";

interface Review {
  id: number;
  reviewer_id: string;
  product_id: string;
  rating: number;
  fake_probability: number | null;
  is_fake: boolean | null;
  verified_purchase: boolean;
}

export default function HistorySection({ className }: { className?: string }) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    fetch(`${API}/api/reviews?limit=20`)
      .then(r => r.json())
      .then(d => { setReviews(d); setLoading(false); })
      .catch(e => { setError(String(e)); setLoading(false); });
  }

  useEffect(() => { load(); }, []);

  return (
    <Section id="history" className={cn(className)}>
      <div className="max-w-container mx-auto flex flex-col gap-12">
        <div className="flex flex-col items-center gap-4 text-center">
          <span className="text-brand text-xs font-bold tracking-widest uppercase">Audit Log</span>
          <h2 className="text-3xl leading-tight font-semibold sm:text-5xl">Recently Analyzed Reviews</h2>
        </div>

        <div className="flex justify-center">
          <button onClick={load} className="bg-card border-border text-muted-foreground hover:text-foreground rounded-lg border px-4 py-2 text-sm font-semibold transition-colors">
            Refresh
          </button>
        </div>

        {error && <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">{error}</div>}
        {loading && <div className="text-muted-foreground text-center text-sm">Loading...</div>}

        {!loading && reviews.length === 0 && !error && (
          <div className="text-muted-foreground text-center text-sm">No reviews analyzed yet. Use the Detect section above.</div>
        )}

        {reviews.length > 0 && (
          <div className="bg-card border-border overflow-hidden rounded-2xl border">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-border border-b">
                    {["ID", "Reviewer", "Product", "Rating", "Fake Prob", "Verdict", "Verified"].map(h => (
                      <th key={h} className="text-muted-foreground px-4 py-3 text-left text-[10px] font-bold tracking-widest uppercase">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {reviews.map((r) => (
                    <tr key={r.id} className="border-border border-b last:border-0 hover:bg-white/[0.02]">
                      <td className="text-muted-foreground px-4 py-3">{r.id}</td>
                      <td className="px-4 py-3 font-mono text-xs">{r.reviewer_id}</td>
                      <td className="px-4 py-3 font-mono text-xs">{r.product_id}</td>
                      <td className="px-4 py-3">{r.rating}★</td>
                      <td className="px-4 py-3">{r.fake_probability != null ? `${(r.fake_probability * 100).toFixed(1)}%` : "N/A"}</td>
                      <td className="px-4 py-3">
                        {r.is_fake == null ? (
                          <span className="text-muted-foreground">—</span>
                        ) : r.is_fake ? (
                          <span className="rounded-full bg-red-500/15 px-2 py-0.5 text-[11px] font-bold text-red-400">FAKE</span>
                        ) : (
                          <span className="rounded-full bg-green-500/15 px-2 py-0.5 text-[11px] font-bold text-green-400">GENUINE</span>
                        )}
                      </td>
                      <td className="px-4 py-3">{r.verified_purchase ? "✅" : "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </Section>
  );
}
