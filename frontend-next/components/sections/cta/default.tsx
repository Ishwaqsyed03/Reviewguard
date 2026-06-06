import { cn } from "@/lib/utils";

import Glow from "../../ui/glow";
import { LinkButton } from "../../ui/link-button";
import { Section } from "../../ui/section";

export default function CTA({ className }: { className?: string }) {
  return (
    <Section className={cn("group relative overflow-hidden", className)}>
      <div className="max-w-container relative z-10 mx-auto flex flex-col items-center gap-6 text-center sm:gap-8">
        <h2 className="max-w-[640px] text-3xl leading-tight font-semibold sm:text-5xl sm:leading-tight">
          Start detecting fake reviews
        </h2>
        <div className="flex justify-center gap-4">
          <LinkButton variant="default" size="lg" href="#detect">Detect a Review Now</LinkButton>
          <LinkButton variant="glow" size="lg" href="http://localhost:8000/docs">API Docs</LinkButton>
        </div>
      </div>
      <div className="absolute top-0 left-0 h-full w-full translate-y-[1rem] opacity-80 transition-all duration-500 ease-in-out group-hover:translate-y-[-2rem] group-hover:opacity-100">
        <Glow variant="bottom" />
      </div>
    </Section>
  );
}
