import { ArrowRightIcon, ShieldCheck } from "lucide-react";
import { ReactNode } from "react";

import { cn } from "@/lib/utils";

import { Badge } from "../../ui/badge";
import Glow from "../../ui/glow";
import { LinkButton, type LinkButtonProps } from "../../ui/link-button";
import { Mockup, MockupFrame } from "../../ui/mockup";
import { Section } from "../../ui/section";

interface HeroButtonProps extends Omit<LinkButtonProps, "children"> {
  text: string;
}

interface HeroProps {
  title?: string;
  description?: string;
  mockup?: ReactNode | false;
  badge?: ReactNode | false;
  buttons?: HeroButtonProps[] | false;
  className?: string;
}

const DEFAULT_HERO_BUTTONS: HeroButtonProps[] = [
  { href: "#detect", text: "Detect a Review", variant: "default" },
  { href: "#how-it-works", text: "How It Works", variant: "glow" },
];

const DEFAULT_HERO_BADGE = (
  <Badge variant="outline" className="animate-appear">
    <span className="text-muted-foreground">Hackathon Project — Fake Review Detection AI</span>
    <a href="#detect" className="flex items-center gap-1">
      Try it now
      <ArrowRightIcon className="size-3" />
    </a>
  </Badge>
);

const DEFAULT_HERO_MOCKUP = (
  <div className="bg-card w-full overflow-hidden relative">
    <div className="bg-muted/50 border-border flex items-center gap-1.5 border-b px-4 py-2.5 z-10 relative">
      <div className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
      <div className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
      <div className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
      <div className="bg-muted text-muted-foreground mx-3 flex h-5 flex-1 items-center rounded px-2 text-[10px] tracking-wide">
        reviewguard.ai/about
      </div>
    </div>
    <div className="p-6 sm:p-10 relative text-left">
      <div className="absolute top-0 right-0 w-64 h-64 bg-brand/10 blur-3xl rounded-full pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-48 h-48 bg-blue-500/10 blur-3xl rounded-full pointer-events-none" />
      
      <div className="relative z-10 flex flex-col gap-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-brand/20 border border-brand/30 shadow-[0_0_15px_rgba(255,138,61,0.2)]">
            <ShieldCheck className="size-6 text-brand" />
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
            Project <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FF8A3D] to-[#FF3B6F]">ReviewGuard</span>
          </h2>
        </div>
        
        <div className="space-y-4 text-muted-foreground text-sm sm:text-base leading-relaxed max-w-3xl">
          <p>
            ReviewGuard is an AI tool that catches fake reviews instantly. 
            It reads the text and analyzes how the user behaves to spot <strong className="text-foreground">warning signs</strong>.
          </p>
          <p>
            Our machine learning model calculates a "fake score" in milliseconds. Most importantly, it doesn’t just give you a number—it gives a <strong className="text-brand">clear explanation</strong> of exactly <i>why</i> a review was flagged, pointing out the suspicious words or actions so you can trust the result.
          </p>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-2">
          {[
            { label: "Speed", value: "Instant" },
            { label: "Warning Signs", value: "17+" },
            { label: "Powered By", value: "Smart AI" },
            { label: "Verdicts", value: "Explainable" }
          ].map(stat => (
            <div key={stat.label} className="bg-background/50 border border-border/50 rounded-xl p-4 text-center hover:bg-background/80 transition-colors shadow-sm">
              <div className="text-transparent bg-clip-text bg-gradient-to-r from-[#FF8A3D] to-[#FF3B6F] text-xl font-black">{stat.value}</div>
              <div className="text-[10px] sm:text-xs text-muted-foreground mt-1.5 uppercase tracking-wider font-semibold">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

export default function Hero({
  title = "Detect Fake Reviews with AI",
  description = "17 text and behavioural signals. Real-time verdicts. Fully explainable results. See their impact on product recommendations.",
  mockup = DEFAULT_HERO_MOCKUP,
  badge = DEFAULT_HERO_BADGE,
  buttons = DEFAULT_HERO_BUTTONS,
  className,
}: HeroProps) {
  return (
    <Section className={cn("fade-bottom overflow-hidden pb-0 sm:pb-0 md:pb-0", className)}>
      <div className="max-w-container mx-auto flex flex-col gap-12 pt-16 sm:gap-24">
        <div className="flex flex-col items-center gap-6 text-center sm:gap-12">
          {badge !== false && badge}
          <h1 className="animate-appear from-foreground to-foreground dark:to-muted-foreground relative z-10 inline-block bg-linear-to-r bg-clip-text text-4xl leading-tight font-semibold text-balance text-transparent drop-shadow-2xl sm:text-6xl sm:leading-tight md:text-8xl md:leading-tight">
            {title}
          </h1>
          <p className="text-md animate-appear text-muted-foreground relative z-10 max-w-[740px] font-medium text-balance opacity-0 delay-100 sm:text-xl">
            {description}
          </p>
          {buttons !== false && buttons.length > 0 && (
            <div className="animate-appear relative z-10 flex justify-center gap-4 opacity-0 delay-300">
              {buttons.map((button) => (
                <LinkButton key={`${button.href}-${button.text}`} variant={button.variant || "default"} size="lg" href={button.href} icon={button.icon} iconRight={button.iconRight}>
                  {button.text}
                </LinkButton>
              ))}
            </div>
          )}
          {mockup !== false && (
            <div className="relative w-full pt-12 group">
              <MockupFrame className="animate-appear opacity-0 delay-700" size="small">
                <Mockup type="responsive" className="bg-background/90 w-full rounded-xl border-0">
                  {mockup}
                </Mockup>
              </MockupFrame>
              <Glow variant="top" className="animate-appear-zoom opacity-0 delay-1000" />
            </div>
          )}
        </div>
      </div>
    </Section>
  );
}
