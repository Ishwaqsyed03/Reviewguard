import React from "react";
import { Section } from "../../ui/section";
import { Database, Binary, Cpu, ShieldCheck, Activity, BrainCircuit, FileSearch, ArrowRight } from "lucide-react";

export default function HowItWorks() {
  return (
    <Section id="how-it-works" className="relative overflow-hidden bg-background py-24">
      {/* Background glow effects */}
      <div className="absolute top-0 left-1/2 -ml-[40rem] w-[80rem] h-[40rem] bg-gradient-to-b from-brand/10 to-transparent opacity-50 blur-3xl pointer-events-none" />
      
      <style>{`
        @keyframes scanline {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(400%); }
        }
        @keyframes pulse-glow {
          0%, 100% { fill: rgba(255, 138, 61, 0.4); filter: drop-shadow(0 0 8px rgba(255,138,61,0.6)); transform: scale(1); }
          50% { fill: rgba(255, 59, 111, 0.8); filter: drop-shadow(0 0 16px rgba(255,59,111,1)); transform: scale(1.1); }
        }
        @keyframes data-flow {
          0% { stroke-dashoffset: 24; }
          100% { stroke-dashoffset: 0; }
        }
        @keyframes float-up {
          0% { opacity: 0; transform: translateY(10px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes type-text {
          0% { width: 0; }
          100% { width: 100%; }
        }
        @keyframes blink-cursor {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
        
        .animate-scan { animation: scanline 3s linear infinite; }
        .data-pipe { 
          stroke-dasharray: 6 6; 
          animation: data-flow 1s linear infinite; 
        }
        .node-pulse { animation: pulse-glow 2s ease-in-out infinite; }
        
        .code-line {
          display: inline-block;
          overflow: hidden;
          white-space: nowrap;
        }
      `}</style>

      <div className="relative z-10 max-w-container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand/10 text-brand text-sm font-semibold mb-6 border border-brand/20 shadow-[0_0_15px_rgba(255,138,61,0.15)]">
            <Activity className="size-4" />
            <span>Behind The Scenes</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
            The Detection <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FF8A3D] to-[#FF3B6F]">Engine</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            ReviewGuard doesn't just guess. It processes every review through a strict 3-stage pipeline combining 
            heuristics, NLP, and a highly-optimized Gradient Boosting Model.
          </p>
        </div>

        {/* Technical Architecture Graphic */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_2fr_1fr] gap-6 items-center">
          
          {/* Stage 1: Ingestion & Extraction */}
          <div className="hover:-translate-y-1 transition-transform duration-300">
            <div className="bg-card border border-border/50 rounded-xl p-6 shadow-2xl relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-br from-brand/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2.5 rounded-lg bg-blue-500/10 text-blue-500 border border-blue-500/20">
                  <Database className="size-6" />
                </div>
                <div>
                  <h3 className="font-bold text-lg">1. Ingestion</h3>
                  <p className="text-xs text-muted-foreground">O(1) Data Parsing</p>
                </div>
              </div>
              
              <div className="space-y-3 mt-6 relative">
                <div className="absolute top-0 left-0 w-full h-[50px] bg-gradient-to-b from-blue-500/20 to-transparent opacity-50 animate-scan pointer-events-none" />
                {["Uppercase Ratio", "Lexical Diversity", "Sentiment Score", "Verified Status"].map((feat, i) => (
                  <div key={i} className="flex justify-between items-center text-sm p-2 rounded bg-background/50 border border-border/30">
                    <span className="text-muted-foreground flex items-center gap-1.5"><Binary className="size-3"/> {feat}</span>
                    <span className="font-mono text-xs text-blue-400 font-semibold" style={{animation: `float-up 0.5s ease forwards ${i * 0.2}s`}}>{(Math.random()).toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Stage 2: ML Inference Core (Centerpiece) */}
          <div className="relative hover:-translate-y-1 transition-transform duration-300 z-10">
            {/* Connecting pipes from left */}
            <div className="hidden lg:block absolute -left-12 top-1/2 w-12 h-[2px] bg-border overflow-hidden">
              <div className="w-full h-full bg-gradient-to-r from-blue-500 to-brand data-pipe" style={{strokeDasharray: '4 4'}} />
            </div>
            
            <div className="bg-card border border-brand/30 rounded-2xl p-8 shadow-[0_0_40px_rgba(255,138,61,0.1)] relative">
              <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-[#FF8A3D] to-[#FF3B6F]" />
              
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="text-xl font-bold tracking-tight flex items-center gap-2">
                    <BrainCircuit className="size-6 text-brand" /> 
                    Gradient Boosting Ensemble
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">17-Dimensional Feature Vector Inference</p>
                </div>
                <div className="px-2 py-1 rounded bg-brand/10 text-brand text-xs font-mono border border-brand/20 flex items-center gap-1">
                  <Activity className="size-3 animate-pulse" /> ~45ms req
                </div>
              </div>

              {/* Pseudo Terminal showing model execution */}
              <div className="bg-[#0b0c10] border border-[#1e212b] rounded-lg p-4 font-mono text-xs sm:text-sm text-[#8a99a8] overflow-hidden relative shadow-inner">
                <div className="flex gap-1.5 mb-3">
                  <div className="w-2.5 h-2.5 rounded-full bg-red-500/80"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-green-500/80"></div>
                </div>
                <div className="space-y-1.5">
                  <div><span className="text-emerald-400">root@reviewguard</span>:~$ ./predict --review_id=98A2B</div>
                  <div className="opacity-0" style={{animation: "float-up 0.1s forwards 0.5s"}}>[INFO] Loading pre-trained model weights... OK</div>
                  <div className="opacity-0" style={{animation: "float-up 0.1s forwards 0.8s"}}>[INFO] Constructing 17-D vector... OK [shape: 1x17]</div>
                  <div className="opacity-0" style={{animation: "float-up 0.1s forwards 1.2s", color: "#61afef"}}>
                     tree_01: weight=0.23, node_split=uppercase_ratio &gt; 0.4
                  </div>
                  <div className="opacity-0" style={{animation: "float-up 0.1s forwards 1.4s", color: "#61afef"}}>
                     tree_02: weight=0.18, node_split=sentiment_polarity &lt; -0.5
                  </div>
                  <div className="opacity-0" style={{animation: "float-up 0.1s forwards 1.8s", color: "#c678dd"}}>
                    {'=>'} Fake Probability: <span className="font-bold text-white">87.4%</span>
                  </div>
                  <div className="opacity-0 flex" style={{animation: "float-up 0.1s forwards 2.0s"}}>
                     <span className="text-emerald-400 mr-2">root@reviewguard</span>:~$ <span className="w-2 h-4 bg-white/70 ml-1 inline-block" style={{animation: "blink-cursor 1s infinite"}}/>
                  </div>
                </div>
              </div>
              
              {/* Animated visual tree abstract */}
              <div className="mt-8 flex justify-center">
                <svg width="180" height="80" viewBox="0 0 180 80">
                  <path d="M90 10 L45 45 M90 10 L135 45 M45 45 L 20 75 M45 45 L 70 75 M135 45 L 110 75 M135 45 L 160 75" className="data-pipe stroke-brand/30" strokeWidth="2" fill="none" />
                  <circle cx="90" cy="10" r="6" className="node-pulse" />
                  <circle cx="45" cy="45" r="5" fill="#4b5563" />
                  <circle cx="135" cy="45" r="5" fill="#4b5563" />
                  <circle cx="20" cy="75" r="4" fill="#374151" />
                  <circle cx="70" cy="75" r="4" fill="#374151" />
                  <circle cx="110" cy="75" r="4" fill="#374151" />
                  <circle cx="160" cy="75" r="4" className="node-pulse" />
                </svg>
              </div>
            </div>
            
            {/* Connecting pipes to right */}
            <div className="hidden lg:block absolute -right-12 top-1/2 w-12 h-[2px] bg-border overflow-hidden">
              <div className="w-full h-full bg-gradient-to-r from-brand to-rose-500 data-pipe" style={{strokeDasharray: '4 4'}} />
            </div>
          </div>

          {/* Stage 3: Explainable Verdict */}
          <div className="hover:-translate-y-1 transition-transform duration-300">
            <div className="bg-card border border-border/50 rounded-xl p-6 shadow-2xl relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-br from-rose-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2.5 rounded-lg bg-rose-500/10 text-rose-500 border border-rose-500/20">
                  <ShieldCheck className="size-6" />
                </div>
                <div>
                  <h3 className="font-bold text-lg">3. Validation</h3>
                  <p className="text-xs text-muted-foreground">Explainable AI (XAI)</p>
                </div>
              </div>

              {/* Fake Confidence Gauge */}
              <div className="py-4 border-y border-border/50 my-4 flex items-center justify-between">
                <div className="space-y-1">
                  <div className="text-sm font-semibold flex items-center gap-1.5"><FileSearch className="size-3"/> Verdict</div>
                  <div className="text-xs text-muted-foreground">Confidence Level</div>
                </div>
                <div className="text-right">
                  <div className="text-xl font-black text-rose-500">FAKE</div>
                  <div className="text-xs font-mono text-rose-500/80">87.4% Match</div>
                </div>
              </div>

              {/* Dominant features */}
              <div className="space-y-2 relative">
                <p className="text-xs font-medium text-muted-foreground mb-3">Top Driving Factors:</p>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-medium">Excessive Uppercase</span>
                      <span className="font-mono text-rose-500">+34%</span>
                    </div>
                    <div className="h-1.5 bg-background rounded-full overflow-hidden">
                      <div className="h-full bg-rose-500 rounded-full w-[85%]" />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-medium">Sudden Cadence</span>
                      <span className="font-mono text-rose-500">+22%</span>
                    </div>
                    <div className="h-1.5 bg-background rounded-full overflow-hidden">
                      <div className="h-full bg-rose-500/70 rounded-full w-[65%]" />
                    </div>
                  </div>
                </div>
              </div>
              
            </div>
          </div>
        </div>
      </div>
    </Section>
  );
}
