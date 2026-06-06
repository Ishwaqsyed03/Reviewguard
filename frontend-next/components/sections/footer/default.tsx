import { Shield } from "lucide-react";

import { cn } from "@/lib/utils";

import { Footer, FooterBottom, FooterColumn, FooterContent } from "../../ui/footer";
import { ModeToggle } from "../../ui/mode-toggle";

export default function FooterSection({ className }: { className?: string }) {
  return (
    <footer className={cn("bg-background w-full px-4", className)}>
      <div className="max-w-container mx-auto">
        <Footer>
          <FooterContent>
            <FooterColumn className="col-span-2 sm:col-span-3 md:col-span-1">
              <div className="flex items-center gap-2">
                <Shield className="size-5 text-brand" />
                <h3 className="text-xl font-bold">ReviewGuard</h3>
              </div>
              <p className="text-muted-foreground text-sm">AI-powered fake review detection.</p>
            </FooterColumn>
            <FooterColumn>
              <h3 className="text-md pt-1 font-semibold">App</h3>
              {[["Detect a Review", "#detect"], ["Recommendations", "#recommendations"], ["Timeline", "#timeline"], ["Audit Log", "#history"]].map(([t, h]) => (
                <a key={h} href={h} className="text-muted-foreground text-sm">{t}</a>
              ))}
            </FooterColumn>
            <FooterColumn>
              <h3 className="text-md pt-1 font-semibold">Learn</h3>
              {[["How It Works", "#how-it-works"], ["Features", "#features"], ["FAQ", "#faq"]].map(([t, h]) => (
                <a key={h} href={h} className="text-muted-foreground text-sm">{t}</a>
              ))}
            </FooterColumn>
            <FooterColumn>
              <h3 className="text-md pt-1 font-semibold">Developers</h3>
              {[["API Docs", "http://localhost:8000/docs"], ["GitHub", "https://github.com"]].map(([t, h]) => (
                <a key={h} href={h} className="text-muted-foreground text-sm">{t}</a>
              ))}
            </FooterColumn>
          </FooterContent>
          <FooterBottom>
            <div>© 2026 ReviewGuard. Hackathon Project.</div>
            <div className="flex items-center gap-4">
              <ModeToggle />
            </div>
          </FooterBottom>
        </Footer>
      </div>
    </footer>
  );
}
