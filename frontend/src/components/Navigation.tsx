"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Orbit,
  Compass,
  Database,
  Cpu,
  Telescope,
  History,
  Layers,
  Settings,
  Radio,
  Sparkles,
  BookOpen,
  Eye,
  Sliders,
} from "lucide-react";
import { api, SystemHealth } from "@/lib/api";
import { useExperienceMode } from "@/context/ModeContext";

const NAV_ITEMS = [
  { href: "/", label: "Landing", icon: Orbit },
  { href: "/space-3d", label: "3D Universe", icon: Compass },
  { href: "/transit-sim", label: "How Planets Are Found", icon: BookOpen },
  { href: "/kepler90", label: "Kepler-90 System", icon: Sparkles },
  { href: "/planet-viewer", label: "3D Planet Inspector", icon: Eye },
  { href: "/detector", label: "AI Detection Lab", icon: Telescope },
  { href: "/studio", label: "Light Curve Studio", icon: Radio },
  { href: "/explorer", label: "NASA DR24 Catalog", icon: Database },
  { href: "/models", label: "Model Intelligence", icon: Cpu },
  { href: "/experiments", label: "Research History", icon: History },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function Navigation() {
  const pathname = usePathname();
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const { mode, toggleMode, quality, setQuality } = useExperienceMode();

  useEffect(() => {
    api.getHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
    const interval = setInterval(() => {
      api.getHealth().then(setHealth).catch(() => setHealth(null));
    }, 20000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-50 border-b border-space-border bg-space-950/95 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Mission Badge */}
          <div className="flex items-center gap-3">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-accent-blue via-accent-purple to-accent-cyan flex items-center justify-center shadow-lg shadow-accent-blue/20 group-hover:scale-105 transition-transform">
                <Orbit className="h-5 w-5 text-space-950 stroke-[2.5]" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold tracking-wider text-base sm:text-lg text-astro-text font-mono">
                    EXOPLANET FINDER
                  </span>
                  <span className="text-[10px] uppercase tracking-widest bg-accent-blue/10 text-accent-blue px-2 py-0.5 rounded border border-accent-blue/30 font-mono">
                    3D AI
                  </span>
                </div>
                <p className="text-[10px] text-astro-muted hidden md:block">
                  Beyond Our Solar System · NASA Kepler DR24
                </p>
              </div>
            </Link>
          </div>

          {/* Right Controls: Mode Toggle, Quality Selector, Telemetry */}
          <div className="flex items-center gap-3 text-xs font-mono">
            {/* Mode Switcher: Explore Mode vs Research Mode */}
            <button
              onClick={toggleMode}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border transition font-bold select-none ${
                mode === "explore"
                  ? "bg-accent-emerald/10 border-accent-emerald/40 text-accent-emerald"
                  : "bg-accent-purple/10 border-accent-purple/40 text-accent-purple"
              }`}
              title="Click to toggle between Beginner-friendly Explore Mode and Advanced Research Mode"
            >
              {mode === "explore" ? (
                <>
                  <Compass className="h-3.5 w-3.5" />
                  <span>EXPLORE MODE</span>
                </>
              ) : (
                <>
                  <Cpu className="h-3.5 w-3.5" />
                  <span>RESEARCH MODE</span>
                </>
              )}
            </button>

            {/* Quality Preset */}
            <div className="hidden sm:flex items-center gap-1 bg-space-850 border border-space-border px-2 py-1 rounded-lg text-astro-muted text-[11px]">
              <span className="text-astro-subtle">3D:</span>
              {(["low", "medium", "high", "ultra"] as const).map((q) => (
                <button
                  key={q}
                  onClick={() => setQuality(q)}
                  className={`px-1.5 py-0.5 rounded uppercase font-mono ${
                    quality === q ? "bg-accent-blue text-space-950 font-bold" : "hover:text-white"
                  }`}
                >
                  {q[0]}
                </button>
              ))}
            </div>

            {/* Hardware Telemetry Indicator */}
            <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full bg-space-850 border border-space-border">
              <span
                className={`h-2 w-2 rounded-full animate-pulse ${
                  health ? "bg-accent-emerald" : "bg-accent-rose"
                }`}
              />
              <span className="text-astro-muted">
                {health ? (
                  <>
                    <span className="text-accent-emerald font-semibold">ONLINE</span> ·{" "}
                    {health.cuda_available ? "RTX 4060 GPU" : "CPU"}
                  </>
                ) : (
                  <span className="text-accent-rose">CONNECTING...</span>
                )}
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Bar Pills */}
        <nav className="flex space-x-1 overflow-x-auto py-2 no-scrollbar border-t border-space-border/50">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-colors ${
                  isActive
                    ? "bg-accent-blue text-space-950 font-bold shadow-md shadow-accent-blue/20"
                    : "text-astro-muted hover:text-astro-text hover:bg-space-800"
                }`}
              >
                <Icon className={`h-3.5 w-3.5 ${isActive ? "text-space-950" : "text-astro-subtle"}`} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
