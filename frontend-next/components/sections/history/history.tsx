"use client";

import { useEffect, useState } from "react";

import { cn } from "@/lib/utils";

import { Section } from "../../ui/section";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Review {
  id: number;
  rating: number;
  fake_probability: number;
  is_fake: boolean;
  verified_purchase: boolean;
  created_at: string;
}

export default function HistorySection({ className }: { className?: string }) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API}/api/reviews?limit=20`);
      if (!response.ok) {
        throw new Error(`History request failed (${response.status})`);
      }
      const data: unknown = await response.json();
      if (!Array.isArray(data)) {
        throw new Error("History response was not a list");
      }
      setReviews(data as Review[]);
    } catch (err) {
      setError(String(err));
      setReviews([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <Section id="history" className={cn(className)}>
      <div className="max-w-container mx-auto flex flex-col gap-12">
        <div className="flex flex-col items-center gap-4 text-center">
          <span className="text-brand text-xs font-bold tracking-widest uppercase">Audit Log</span>
          <h2 className="text-3xl leading-tight font-semibold sm:text-5xl">Recently Analyzed Reviews</h2>
          <p className="text-muted-foreground max-w-[600px] text-sm">
            The public history shows summary results only. Review text and submitted IDs are not returned.
          </p>
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
                    {["Analysis", "Date", "Rating", "Fake Prob", "Verdict", "Verified"].map(h => (
                      <th key={h} className="text-muted-foreground px-4 py-3 text-left text-[10px] font-bold tracking-widest uppercase">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {reviews.map((review) => (
                    <tr key={review.id} className="border-border border-b last:border-0 hover:bg-white/[0.02]">
                      <td className="text-muted-foreground px-4 py-3">#{review.id}</td>
                      <td className="text-muted-foreground px-4 py-3">{new Date(review.created_at).toLocaleString()}</td>
                      <td className="px-4 py-3">{review.rating}★</td>
                      <td className="px-4 py-3">{(review.fake_probability * 100).toFixed(1)}%</td>
                      <td className="px-4 py-3">
                        {review.is_fake ? (
                          <span className="rounded-full bg-red-500/15 px-2 py-0.5 text-[11px] font-bold text-red-400">FAKE</span>
                        ) : (
                          <span className="rounded-full bg-green-500/15 px-2 py-0.5 text-[11px] font-bold text-green-400">GENUINE</span>
                        )}
                      </td>
                      <td className="px-4 py-3">{review.verified_purchase ? "✅" : "—"}</td>
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
