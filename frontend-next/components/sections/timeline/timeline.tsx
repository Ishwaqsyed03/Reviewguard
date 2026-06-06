"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { cn } from "@/lib/utils";

import { Section } from "../../ui/section";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const PRODUCTS = {
  "Sony WH-1000XM5 Headphones": "biz_001",
  "Ninja Air Fryer XL":         "biz_004",
  "Apple AirPods Pro":          "biz_009",
};

interface DailyRow { date: string; avg_rating: number; genuine_avg: number; fake_count: number; }
interface TimelineData {
  total_genuine: number;
  total_fake: number;
  rating_during_bomb: number;
  rating_genuine_only: number;
  bomb_start: string;
  bomb_end: string;
  daily: DailyRow[];
}

export default function TimelineSection({ className }: { className?: string }) {
  const [selected, setSelected] = useState<keyof typeof PRODUCTS>("Sony WH-1000XM5 Headphones");
  const [data, setData] = useState<TimelineData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const pid = PRODUCTS[selected];
    setData(null);
    fetch(`${API}/api/timeline?product_id=${pid}`)
      .then(r => r.json())
      .then(setData)
      .catch(e => setError(String(e)));
  }, [selected]);

  return (
    <Section id="timeline" className={cn(className)}>
      <div className="max-w-container mx-auto flex flex-col gap-12">
        <div className="flex flex-col items-center gap-4 text-center">
          <span className="text-brand text-xs font-bold tracking-widest uppercase">Attack Detection</span>
          <h2 className="text-3xl leading-tight font-semibold sm:text-5xl">Review Bombing Timeline</h2>
          <p className="text-muted-foreground max-w-[600px] font-medium">
            A coordinated group posts dozens of fake 5-star reviews within hours, artificially inflating a product rating.
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-3">
          {(Object.keys(PRODUCTS) as (keyof typeof PRODUCTS)[]).map((name) => (
            <button
              key={name}
              onClick={() => setSelected(name)}
              className={cn(
                "border-border rounded-lg border px-4 py-2 text-sm font-semibold transition-colors",
                selected === name ? "bg-primary text-primary-foreground border-primary" : "bg-card text-muted-foreground hover:text-foreground"
              )}
            >
              {name}
            </button>
          ))}
        </div>

        {error && <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">{error}</div>}

        {data && (
          <>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {[
                { label: "Genuine Reviews", value: data.total_genuine, color: "text-green-400" },
                { label: "Fake Injected", value: `+${data.total_fake} in 48hrs`, color: "text-red-400" },
                { label: "Rating During Attack", value: `${data.rating_during_bomb}★`, color: "text-brand" },
                { label: "True Rating", value: `${data.rating_genuine_only}★`, color: "text-foreground" },
              ].map(({ label, value, color }) => (
                <div key={label} className="bg-card border-border rounded-xl border p-4">
                  <div className="text-muted-foreground mb-1 text-[10px] font-bold tracking-widest uppercase">{label}</div>
                  <div className={cn("text-2xl font-bold", color)}>{value}</div>
                </div>
              ))}
            </div>

            <div className="bg-card border-border rounded-2xl border p-4 sm:p-6">
              <h3 className="mb-4 font-semibold">90-Day Review History: {selected}</h3>
              <ResponsiveContainer width="100%" height={360}>
                <ComposedChart data={data.daily} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#a1a1aa" }} tickFormatter={d => d.slice(5)} />
                  <YAxis yAxisId="left" domain={[1, 5.5]} tick={{ fontSize: 10, fill: "#a1a1aa" }} tickFormatter={v => `${v}★`} />
                  <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: "#a1a1aa" }} />
                  <Tooltip contentStyle={{ background: "#1c1c1f", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <ReferenceLine yAxisId="left" x={data.bomb_start} stroke="#f87171" strokeDasharray="4 4" label={{ value: "Attack", fill: "#f87171", fontSize: 10 }} />
                  <ReferenceLine yAxisId="left" x={data.bomb_end} stroke="#f87171" strokeDasharray="4 4" />
                  <Bar yAxisId="right" dataKey="fake_count" name="Fake Reviews Posted" fill="#f0a56540" radius={[3, 3, 0, 0]} />
                  <Line yAxisId="left" type="monotone" dataKey="avg_rating" name="Displayed Rating (incl. fakes)" stroke="#f0a565" strokeWidth={2} dot={false} strokeDasharray="5 3" />
                  <Line yAxisId="left" type="monotone" dataKey="genuine_avg" name="True Rating (genuine only)" stroke="#4ade80" strokeWidth={2} dot={false} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            <div className="border-brand/30 bg-brand/5 rounded-lg border p-4 text-sm text-center">
              The attack inflated the displayed rating by <strong>{(data.rating_during_bomb - data.rating_genuine_only).toFixed(2)} stars</strong> during 48 hours. ReviewGuard flags these in real time.
            </div>
          </>
        )}

        {!data && !error && (
          <div className="text-muted-foreground text-center text-sm">Loading timeline...</div>
        )}
      </div>
    </Section>
  );
}
