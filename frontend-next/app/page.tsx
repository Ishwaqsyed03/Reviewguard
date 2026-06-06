import CTA from "../components/sections/cta/default";
import DetectSection from "../components/sections/detect/detect";
import FAQ from "../components/sections/faq/default";
import Footer from "../components/sections/footer/default";
import Hero from "../components/sections/hero/default";
import HowItWorks from "../components/sections/how-it-works/default";
import HistorySection from "../components/sections/history/history";
import Items from "../components/sections/items/default";
import Logos from "../components/sections/logos/default";
import Navbar from "../components/sections/navbar/default";
import Pricing from "../components/sections/pricing/default";
import RecommendationsSection from "../components/sections/recommendations/recommendations";
import Stats from "../components/sections/stats/default";
import TimelineSection from "../components/sections/timeline/timeline";
import { LayoutLines } from "../components/ui/layout-lines";

export default function Home() {
  return (
    <main className="bg-background text-foreground min-h-screen w-full">
      <LayoutLines />
      <Navbar />
      <Hero />
      <HowItWorks />
      <Logos />
      <Stats />
      <Items />
      <DetectSection />
      <RecommendationsSection />
      <TimelineSection />
      <HistorySection />
      <FAQ />
      <CTA />
      <Footer />
    </main>
  );
}
