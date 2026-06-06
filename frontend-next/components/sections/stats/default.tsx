"use client";

import { useEffect, useState } from "react";

import { Section } from "../../ui/section";

const API = "http://localhost:8000";

interface StatsData { total: number; fake: number; genuine: number; fake_rate: number; }

export default function Stats({ className }: { className?: string }) {
  const [stats, setStats] = useState<StatsData | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/stats`)
      .then(r => r.json())
      .then(setStats)
      .catch(() => setError(true));
  }, []);

  const items = stats ? [
    { label: "Reviews Analyzed", value: stats.total.toLocaleString(), color: "from-foreground dark:to-brand", desc: "total processed" },
    { label: "Fake Detected", value: stats.fake.toLocaleString(), color: "from-red-400 to-red-600", desc: "flagged by model" },
    { label: "Genuine", value: stats.genuine.toLocaleString(), color: "from-green-400 to-green-600", desc: "passed review" },
    { label: "Fake Rate", value: `${(stats.fake_rate * 100).toFixed(1)}%`, color: "from-foreground dark:to-brand", desc: "of total reviews" },
  ] : [
    { label: "Reviews Analyzed", value: "2,847", color: "from-foreground dark:to-brand", desc: "total processed" },
    { label: "Fake Detected", value: "312", color: "from-red-400 to-red-600", desc: "flagged by model" },
    { label: "Genuine", value: "2,535", color: "from-green-400 to-green-600", desc: "passed review" },
    { label: "Fake Rate", value: "11.0%", color: "from-foreground dark:to-brand", desc: "of total reviews" },
  ];

  if (error) return null;

  return (
    <Section className={className}>
      <div className="container mx-auto max-w-[960px]">
        <div className="grid grid-cols-2 gap-12 sm:grid-cols-4">
          {items.map((item) => (
            <div key={item.label} className="flex flex-col items-start gap-3 text-left">
              <div className="text-muted-foreground text-sm font-semibold">{item.label}</div>
              <div className={`bg-linear-to-r ${item.color} bg-clip-text text-4xl font-medium text-transparent drop-shadow-[2px_1px_24px_var(--brand-foreground)] transition-all duration-300 sm:text-5xl md:text-6xl`}>
                {item.value}
              </div>
              <div className="text-muted-foreground text-sm font-semibold text-pretty">{item.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}
