import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "../../ui/accordion";
import { Section } from "../../ui/section";

const ITEMS = [
  {
    q: "How does ReviewGuard detect fake reviews?",
    a: "ReviewGuard extracts 17 text and behavioural signals from each review. Text signals include uppercase ratio, exclamation count, sentiment polarity, unique word ratio, and review length. Behavioural signals include account age, total reviews written, verified purchase status, and helpful votes. A GradientBoosting classifier combines all signals into a fake probability score.",
  },
  {
    q: "What do the probability thresholds mean?",
    a: "Reviews scoring above 70% are flagged as Fake. Scores between 40-70% are marked Suspicious and may need manual review. Scores below 40% are classified as Likely Genuine. Thresholds are tuned to minimize false positives.",
  },
  {
    q: "What is a review bombing attack?",
    a: "A review bombing attack is when a coordinated group posts dozens of fake reviews within a short window — typically 24-48 hours — to artificially inflate or deflate a product rating. The Timeline tab visualises these attack windows and shows the rating distortion.",
  },
  {
    q: "How does fake review filtering affect recommendations?",
    a: "ReviewGuard uses a Bayesian average scoring system weighted by review volume. When fake reviews are injected, they inflate scores and push products unfairly to the top. The Recommendations section compares rankings before and after filtering.",
  },
  {
    q: "Can I train the model on my own dataset?",
    a: "Yes — the backend exposes a /api/train endpoint that retrains the GradientBoosting model on a real-world review dataset. Training takes under 30 seconds and immediately updates the live detection endpoint.",
  },
  {
    q: "What tech stack does ReviewGuard use?",
    a: "Backend: Python 3.10, FastAPI, scikit-learn GradientBoosting, SQLite + SQLAlchemy. Frontend: Next.js 16, TypeScript, Tailwind CSS v4, shadcn/ui components, Launch UI design system.",
  },
];

export default function FAQ({ className }: { className?: string }) {
  return (
    <Section id="faq" className={className}>
      <div className="max-w-container mx-auto flex flex-col items-center gap-8">
        <h2 className="text-center text-3xl font-semibold sm:text-5xl">Questions and Answers</h2>
        <Accordion type="single" collapsible className="w-full max-w-[800px]">
          {ITEMS.map((item, i) => (
            <AccordionItem key={i} value={`item-${i}`}>
              <AccordionTrigger>{item.q}</AccordionTrigger>
              <AccordionContent>
                <p className="text-muted-foreground max-w-[640px] text-balance">{item.a}</p>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </Section>
  );
}
