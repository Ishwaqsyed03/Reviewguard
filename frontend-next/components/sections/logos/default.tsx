import { Badge } from "../../ui/badge";
import { Section } from "../../ui/section";

function TechPill({ name, emoji }: { name: string; emoji: string }) {
  return (
    <div className="border-border bg-card flex items-center gap-2 rounded-full border px-4 py-2">
      <span className="text-lg">{emoji}</span>
      <span className="text-muted-foreground text-sm font-semibold">{name}</span>
    </div>
  );
}

export default function Logos({ className }: { className?: string }) {
  return (
    <Section className={className}>
      <div className="max-w-container mx-auto flex flex-col items-center gap-8 text-center">
        <div className="flex flex-col items-center gap-4">
          <Badge variant="outline" className="border-brand/30 text-brand">Hackathon Project — Jun 2026</Badge>
          <h2 className="text-md font-semibold sm:text-2xl">Built with battle-tested ML and web technologies</h2>
        </div>
        <div className="flex flex-wrap items-center justify-center gap-3">
          <TechPill name="Python 3.10" emoji="🐍" />
          <TechPill name="FastAPI" emoji="⚡" />
          <TechPill name="scikit-learn" emoji="🤖" />
          <TechPill name="SQLite" emoji="🗄️" />
          <TechPill name="Next.js 16" emoji="▲" />
          <TechPill name="Tailwind CSS v4" emoji="🎨" />
        </div>
      </div>
    </Section>
  );
}
