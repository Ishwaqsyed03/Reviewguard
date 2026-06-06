import {
  AlertTriangleIcon, BarChart2Icon, BrainIcon, ClockIcon,
  SearchIcon, ShieldCheckIcon, TrendingUpIcon, ZapIcon,
} from "lucide-react";

import { Item, ItemDescription, ItemIcon, ItemTitle } from "../../ui/item";
import { Section } from "../../ui/section";

const ITEMS = [
  { title: "17-Signal Detection", description: "Text features, sentiment, uppercase ratio, exclamation marks, unique word ratio, review length and more", icon: <SearchIcon className="size-5 stroke-1" /> },
  { title: "Behavioural Analysis", description: "Account age, review count, verified purchase status, helpful votes, and rating patterns", icon: <BrainIcon className="size-5 stroke-1" /> },
  { title: "Real-Time Verdicts", description: "Instant fake probability scores with confidence levels: genuine, suspicious, or fake", icon: <ZapIcon className="size-5 stroke-1" /> },
  { title: "Explainable Results", description: "Every verdict comes with the exact signals that triggered it — no black box decisions", icon: <ShieldCheckIcon className="size-5 stroke-1" /> },
  { title: "Review Bombing Detection", description: "Identify coordinated attack windows where fake reviews spike within hours", icon: <AlertTriangleIcon className="size-5 stroke-1" /> },
  { title: "Ranking Impact", description: "See how fake reviews distort product rankings and restore honest recommendations", icon: <TrendingUpIcon className="size-5 stroke-1" /> },
  { title: "Timeline Analysis", description: "90-day history charts comparing displayed ratings vs. genuine-only ratings", icon: <ClockIcon className="size-5 stroke-1" /> },
  { title: "Audit Log", description: "Full history of all analyzed reviews with verdicts, probabilities, and breakdown", icon: <BarChart2Icon className="size-5 stroke-1" /> },
];

export default function Items({ className }: { className?: string }) {
  return (
    <Section id="features" className={className}>
      <div className="max-w-container mx-auto flex flex-col items-center gap-6 sm:gap-20">
        <h2 className="max-w-[560px] text-center text-3xl leading-tight font-semibold sm:text-5xl sm:leading-tight">
          Everything you need to fight fake reviews.
        </h2>
        <div className="grid auto-rows-fr grid-cols-2 gap-0 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4">
          {ITEMS.map((item) => (
            <Item key={item.title}>
              <ItemTitle className="flex items-center gap-2">
                <ItemIcon>{item.icon}</ItemIcon>
                {item.title}
              </ItemTitle>
              <ItemDescription>{item.description}</ItemDescription>
            </Item>
          ))}
        </div>
      </div>
    </Section>
  );
}
