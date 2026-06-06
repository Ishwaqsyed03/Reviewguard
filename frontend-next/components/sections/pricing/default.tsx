import { BrainIcon, SearchIcon, ShieldCheckIcon } from "lucide-react";

import { cn } from "@/lib/utils";

import { PricingColumn } from "../../ui/pricing-column";
import { Section } from "../../ui/section";

const STEPS = [
  {
    name: "Step 1", icon: <SearchIcon className="size-4" />,
    description: "Paste any review with reviewer metadata into the detection form",
    price: 0, priceNote: "No account needed. Works instantly.",
    cta: { variant: "glow" as const, label: "Try the Detector", href: "#detect" },
    features: ["Review text analysis", "Reviewer behaviour signals", "Star rating & verified purchase check"],
    variant: "default" as const,
  },
  {
    name: "Step 2", icon: <BrainIcon className="size-4" />,
    description: "GradientBoosting model scores all 17 signals and computes a fake probability",
    price: 0, priceNote: "Real-time inference. Sub-second response.",
    cta: { variant: "default" as const, label: "See the Detection", href: "#detect" },
    features: ["17-feature extraction", "GradientBoosting classifier", "Confidence score 0-100%", "Feature importance ranking"],
    variant: "glow-brand" as const,
  },
  {
    name: "Step 3", icon: <ShieldCheckIcon className="size-4" />,
    description: "Get a full verdict with explanation and see the impact on product recommendations",
    price: 0, priceNote: "Every decision is explainable.",
    cta: { variant: "glow" as const, label: "View Recommendations", href: "#recommendations" },
    features: ["Verdict: Genuine / Suspicious / Fake", "Top red-flag signals explained", "Ranking impact analysis"],
    variant: "glow" as const,
  },
];

export default function Pricing({ className = "" }: { className?: string }) {
  return (
    <Section id="how-it-works" className={cn(className)}>
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-12">
        <div className="flex flex-col items-center gap-4 px-4 text-center sm:gap-8">
          <h2 className="text-3xl leading-tight font-semibold sm:text-5xl sm:leading-tight">How ReviewGuard works.</h2>
          <p className="text-md text-muted-foreground max-w-[600px] font-medium sm:text-xl">Three steps from raw review to verdict. No black boxes. Every decision is explainable.</p>
        </div>
        <div className="max-w-container mx-auto grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {STEPS.map((s) => (
            <PricingColumn key={s.name} name={s.name} icon={s.icon} description={s.description}
              price={s.price} priceNote={s.priceNote} cta={s.cta} features={s.features} variant={s.variant} />
          ))}
        </div>
      </div>
    </Section>
  );
}
