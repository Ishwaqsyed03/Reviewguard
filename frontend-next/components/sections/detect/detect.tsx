"use client";

import { useState } from "react";

import { cn } from "@/lib/utils";

import { Section } from "../../ui/section";

const API = "http://localhost:8000";

const PRESETS = {
  fake: {
    text: "BEST PRODUCT EVER!!! AMAZING!!! MUST BUY NOW!!! PERFECT PERFECT PERFECT!!!",
    rating: 5, verified: false, review_count: 2, days_since_joined: 3, helpful_votes: 0,
  },
  genuine: {
    text: "Bought this three weeks ago. Battery life is solid, around 18 hours with moderate use. Build quality feels premium. Noise cancellation handles office noise well but struggles with loud environments. Worth the price for frequent travellers.",
    rating: 4, verified: true, review_count: 47, days_since_joined: 730, helpful_votes: 12,
  },
  borderline: {
    text: "Really happy with this product! Works great and arrived fast. Would recommend to friends.",
    rating: 5, verified: false, review_count: 8, days_since_joined: 45, helpful_votes: 1,
  },
};

const CONTEXT_MAP: Record<string, (v: number) => string> = {
  uppercase_ratio:        (v) => `${(v*100).toFixed(0)}% UPPERCASE text (normal <5%)`,
  exclamation_count:      (v) => `${v.toFixed(0)} exclamation marks (normal: 0-1)`,
  sentiment_subjectivity: (v) => `Subjectivity score ${v.toFixed(2)}/1.0`,
  sentiment_polarity:     (v) => `Extreme positive sentiment: ${v.toFixed(2)}/1.0`,
  unique_word_ratio:      (v) => `Only ${(v*100).toFixed(0)}% unique words - repetitive text`,
  review_count:           (v) => `Account has only ${v.toFixed(0)} total reviews`,
  days_since_joined:      (v) => `Account only ${v.toFixed(0)} days old`,
  helpful_votes:          (v) => `Received ${v.toFixed(0)} helpful votes`,
  verified_purchase:      (v) => v === 0 ? "Not a verified purchase" : "Verified purchase",
  avg_rating_given:       (v) => `Always gives ${v.toFixed(1)}-star ratings`,
  review_length:          (v) => `Review is only ${v.toFixed(0)} characters`,
  word_count:             (v) => `Only ${v.toFixed(0)} words in review`,
};

interface ExplanationItem {
  feature: string;
  label: string;
  value: number;
  score: number;
}

interface DetectResult {
  fake_probability: number;
  is_fake: boolean;
  explanation: ExplanationItem[];
}

export default function DetectSection({ className }: { className?: string }) {
  const [preset, setPreset] = useState<keyof typeof PRESETS>("genuine");
  const [reviewerId, setReviewerId] = useState("user_1234");
  const [productId, setProductId] = useState("prod_456");
  const [rating, setRating] = useState(4);
  const [verified, setVerified] = useState(true);
  const [reviewCount, setReviewCount] = useState(47);
  const [days, setDays] = useState(730);
  const [helpful, setHelpful] = useState(12);
  const [text, setText] = useState(PRESETS.genuine.text);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DetectResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  function loadPreset(key: keyof typeof PRESETS) {
    const p = PRESETS[key];
    setPreset(key);
    setRating(p.rating);
    setVerified(p.verified);
    setReviewCount(p.review_count);
    setDays(p.days_since_joined);
    setHelpful(p.helpful_votes);
    setText(p.text);
    setResult(null);
    setError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API}/api/detect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reviewer_id: reviewerId,
          product_id: productId,
          review_text: text,
          rating,
          verified_purchase: verified,
          review_count: reviewCount,
          days_since_joined: days,
          helpful_votes: helpful,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      setResult(await res.json());
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  const prob = result?.fake_probability ?? 0;
  const verdictColor = prob >= 0.7 ? "text-red-400" : prob >= 0.4 ? "text-yellow-400" : "text-green-400";
  const verdictBg = prob >= 0.7 ? "bg-red-500/10 border-red-500/30" : prob >= 0.4 ? "bg-yellow-500/10 border-yellow-500/30" : "bg-green-500/10 border-green-500/30";
  const verdictLabel = prob >= 0.7 ? "FAKE REVIEW" : prob >= 0.4 ? "SUSPICIOUS" : "LIKELY GENUINE";
  const verdictIcon = prob >= 0.7 ? "🚫" : prob >= 0.4 ? "⚠️" : "✅";

  const fakeSigs = result?.explanation.filter(f => f.score > 0.001).slice(0, 4) ?? [];
  const genuineSigs = result?.explanation.filter(f => f.score < -0.001).slice(0, 2) ?? [];

  return (
    <Section id="detect" className={cn(className)}>
      <div className="max-w-container mx-auto flex flex-col gap-12">
        <div className="flex flex-col items-center gap-4 text-center">
          <span className="text-brand text-xs font-bold tracking-widest uppercase">Detection Engine</span>
          <h2 className="text-3xl leading-tight font-semibold sm:text-5xl">Analyze a Review</h2>
          <p className="text-muted-foreground max-w-[600px] font-medium">
            Paste any review and reviewer info to get an AI verdict with full explanation.
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-3">
          {(["fake", "genuine", "borderline"] as const).map((k) => (
            <button
              key={k}
              onClick={() => loadPreset(k)}
              className={cn(
                "border-border rounded-lg border px-4 py-2 text-sm font-semibold transition-colors",
                preset === k
                  ? "bg-primary text-primary-foreground border-primary"
                  : "bg-card text-muted-foreground hover:text-foreground"
              )}
            >
              Load {k.charAt(0).toUpperCase() + k.slice(1)} Example
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="bg-card border-border rounded-2xl border p-6 sm:p-8">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div className="flex flex-col gap-4">
              {([
                { label: "Reviewer ID", value: reviewerId, set: setReviewerId },
                { label: "Product ID", value: productId, set: setProductId },
              ] as { label: string; value: string; set: (v: string) => void }[]).map(({ label, value, set }) => (
                <div key={label} className="flex flex-col gap-2">
                  <label className="text-muted-foreground text-[10px] font-bold tracking-widest uppercase">{label}</label>
                  <input
                    type="text"
                    value={value}
                    onChange={e => set(e.target.value)}
                    className="bg-background border-border focus:border-brand rounded-lg border px-3 py-2 text-sm transition-colors focus:outline-none"
                  />
                </div>
              ))}
              <div className="flex flex-col gap-2">
                <label className="text-muted-foreground text-[10px] font-bold tracking-widest uppercase">Star Rating: {rating}★</label>
                <input type="range" min={1} max={5} step={0.5} value={rating} onChange={e => setRating(Number(e.target.value))} className="accent-brand w-full" />
              </div>
              <label className="flex cursor-pointer items-center gap-3">
                <input type="checkbox" checked={verified} onChange={e => setVerified(e.target.checked)} className="accent-brand size-4" />
                <span className="text-sm font-semibold">Verified Purchase</span>
              </label>
            </div>
            <div className="flex flex-col gap-4">
              {([
                { label: "Total reviews written", value: reviewCount, set: setReviewCount },
                { label: "Account age (days)", value: days, set: setDays },
                { label: "Helpful votes received", value: helpful, set: setHelpful },
              ] as { label: string; value: number; set: (v: number) => void }[]).map(({ label, value, set }) => (
                <div key={label} className="flex flex-col gap-2">
                  <label className="text-muted-foreground text-[10px] font-bold tracking-widest uppercase">{label}</label>
                  <input
                    type="number"
                    value={value}
                    onChange={e => set(Number(e.target.value))}
                    className="bg-background border-border focus:border-brand rounded-lg border px-3 py-2 text-sm transition-colors focus:outline-none"
                  />
                </div>
              ))}
            </div>
          </div>
          <div className="mt-6 flex flex-col gap-2">
            <label className="text-muted-foreground text-[10px] font-bold tracking-widest uppercase">Review Text</label>
            <textarea
              value={text}
              onChange={e => setText(e.target.value)}
              rows={5}
              className="bg-background border-border focus:border-brand rounded-lg border px-3 py-2 text-sm transition-colors focus:outline-none"
            />
          </div>
          <div className="mt-6 flex justify-center">
            <button
              type="submit"
              disabled={loading}
              className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-lg px-8 py-3 text-sm font-bold transition-opacity disabled:opacity-50"
            >
              {loading ? "Analyzing..." : "Analyze Review"}
            </button>
          </div>
        </form>

        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
            Could not connect to API: {error}
          </div>
        )}

        {result && (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div className={cn("flex flex-col items-center gap-4 rounded-2xl border p-8 text-center", verdictBg)}>
              <div className="text-5xl">{verdictIcon}</div>
              <div className={cn("text-5xl font-black", verdictColor)}>{(prob * 100).toFixed(0)}%</div>
              <div className={cn("text-sm font-bold tracking-widest uppercase", verdictColor)}>{verdictLabel}</div>
              <div className="bg-muted h-2 w-full overflow-hidden rounded-full">
                <div
                  className={cn("h-full rounded-full transition-all duration-700", prob >= 0.7 ? "bg-red-500" : prob >= 0.4 ? "bg-yellow-400" : "bg-green-500")}
                  style={{ width: `${prob * 100}%` }}
                />
              </div>
              <p className="text-muted-foreground text-xs">Above 70% = fake · 40-70% = suspicious · Below 40% = genuine</p>
            </div>
            <div className="bg-card border-border flex flex-col gap-4 rounded-2xl border p-6">
              <h3 className="text-sm font-bold">What triggered this verdict?</h3>
              {fakeSigs.length > 0 && (
                <div className="flex flex-col gap-2">
                  <span className="text-muted-foreground text-[10px] font-bold tracking-widest uppercase">Red flags</span>
                  {fakeSigs.map((f) => {
                    const fn = CONTEXT_MAP[f.feature];
                    const ctx = fn ? fn(f.value) : `${f.label}: ${f.value.toFixed(2)}`;
                    return <div key={f.feature} className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-400">🚩 {ctx}</div>;
                  })}
                </div>
              )}
              {genuineSigs.length > 0 && (
                <div className="flex flex-col gap-2">
                  <span className="text-muted-foreground text-[10px] font-bold tracking-widest uppercase">Genuine signals</span>
                  {genuineSigs.map((f) => {
                    const fn = CONTEXT_MAP[f.feature];
                    const ctx = fn ? fn(f.value) : `${f.label}: ${f.value.toFixed(2)}`;
                    return <div key={f.feature} className="rounded-lg border border-green-500/30 bg-green-500/10 px-3 py-2 text-xs text-green-400">✅ {ctx}</div>;
                  })}
                </div>
              )}
              {fakeSigs.length === 0 && genuineSigs.length === 0 && (
                <p className="text-muted-foreground text-sm">No strong signals found.</p>
              )}
            </div>
          </div>
        )}
      </div>
    </Section>
  );
}
