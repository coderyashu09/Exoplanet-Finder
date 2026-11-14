"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Compass,
  Sparkles,
  Telescope,
  Globe,
  Radio,
  ArrowRight,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { api, Kepler90System } from "@/lib/api";

export default function Kepler90Page() {
  const [system, setSystem] = useState<Kepler90System | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getKepler90()
      .then(setSystem)
      .catch((err) => console.error("Error loading Kepler-90", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="border-b border-space-border pb-4">
        <div className="inline-flex items-center gap-2 rounded-full border border-accent-emerald/30 bg-accent-emerald/10 px-3 py-1 text-xs font-mono text-accent-emerald mb-2">
          <Sparkles className="h-3.5 w-3.5" />
          <span>HISTORIC AI EXOPLANET MILESTONE · 8-PLANET STAR SYSTEM</span>
        </div>
        <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-astro-text flex items-center gap-3">
          <Compass className="h-8 w-8 text-accent-blue" />
          Kepler-90 Star System Explorer (KIC 11442793)
        </h1>
        <p className="text-xs sm:text-sm text-astro-muted mt-1">
          The first extrasolar planetary system discovered with 8 orbiting planets—matching our Solar System
        </p>
      </div>

      {/* Hero AI Discovery Spotlight */}
      <div className="relative overflow-hidden rounded-2xl border border-accent-emerald/40 bg-gradient-to-br from-space-850 via-space-900 to-space-950 p-6 sm:p-8 shadow-xl">
        <div className="max-w-3xl space-y-4">
          <div className="flex items-center gap-2 text-accent-emerald font-mono text-xs font-bold uppercase tracking-wider">
            <span>NASA / Google AI Discovery (December 2017)</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-astro-text">
            How a 1D Convolutional Neural Network Uncovered Kepler-90i
          </h2>
          <p className="text-xs sm:text-sm text-astro-muted leading-relaxed">
            Kepler-90 was originally known to have 7 transiting planets. In 2017, Christopher Shallue (Senior AI Engineer at Google AI) and Andrew Vanderburg (NASA Sagan Postdoctoral Fellow) trained a two-view 1D Convolutional Neural Network on 15,000 Kepler signals. They tasked the AI with reviewing 670 multi-planet stars with weak, overlooked candidate dips.
          </p>
          <p className="text-xs sm:text-sm text-astro-muted leading-relaxed">
            The neural network successfully detected an ultra-weak 14.4-day periodic dip with a signal-to-noise ratio of only <strong className="text-accent-emerald">8.7</strong>—confirming the presence of <strong className="text-white">Kepler-90i</strong>, an incandescent rocky planet 1.32× the radius of Earth with a blistering surface temperature of ~709 K.
          </p>

          <div className="flex flex-wrap gap-3 pt-2">
            <Link
              href="/detector?kepid=11442793&period=7.008&duration=3.0&depth=340"
              className="inline-flex items-center gap-2 rounded-lg bg-accent-blue px-4 py-2 text-xs font-mono font-bold text-space-950 hover:bg-accent-blue/90 transition"
            >
              <Telescope className="h-3.5 w-3.5" />
              Analyze Kepler-90 in Lab
            </Link>
            <Link
              href="/space-3d"
              className="inline-flex items-center gap-2 rounded-lg border border-space-border bg-space-800 px-4 py-2 text-xs font-mono font-medium text-astro-text hover:bg-space-700 transition"
            >
              Open 3D Orbital Simulator
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Host Star & Scale Comparison Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Host Star Card */}
        <div className="rounded-xl border border-space-border bg-space-850 p-6 space-y-4">
          <h3 className="text-sm font-semibold text-astro-text font-mono uppercase tracking-wider flex items-center gap-2">
            <Globe className="h-4 w-4 text-accent-gold" />
            Host Star Characteristics
          </h3>

          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between border-b border-space-border/50 pb-2">
              <span className="text-astro-muted">Target Name:</span>
              <span className="text-astro-text font-bold">Kepler-90 (KOI-351)</span>
            </div>
            <div className="flex justify-between border-b border-space-border/50 pb-2">
              <span className="text-astro-muted">Kepler ID (KIC):</span>
              <span className="text-accent-blue font-bold">11442793</span>
            </div>
            <div className="flex justify-between border-b border-space-border/50 pb-2">
              <span className="text-astro-muted">Spectral Class:</span>
              <span className="text-accent-gold">G0V Main Sequence</span>
            </div>
            <div className="flex justify-between border-b border-space-border/50 pb-2">
              <span className="text-astro-muted">Stellar Mass:</span>
              <span className="text-astro-text">1.20 M☉ (1.20x Sun)</span>
            </div>
            <div className="flex justify-between border-b border-space-border/50 pb-2">
              <span className="text-astro-muted">Stellar Radius:</span>
              <span className="text-astro-text">1.20 R☉ (1.20x Sun)</span>
            </div>
            <div className="flex justify-between border-b border-space-border/50 pb-2">
              <span className="text-astro-muted">Effective Temp:</span>
              <span className="text-astro-text">6,080 K</span>
            </div>
            <div className="flex justify-between">
              <span className="text-astro-muted">Distance:</span>
              <span className="text-astro-text">~2,840 Light-Years</span>
            </div>
          </div>
        </div>

        {/* Solar System Architectural Scale Comparison */}
        <div className="lg:col-span-2 rounded-xl border border-space-border bg-space-850 p-6 space-y-4">
          <h3 className="text-sm font-semibold text-astro-text font-mono uppercase tracking-wider flex items-center gap-2">
            <Zap className="h-4 w-4 text-accent-purple" />
            Solar System Scale Comparison
          </h3>

          <div className="rounded-lg bg-space-900 border border-space-border p-4 text-xs font-mono text-astro-muted space-y-2">
            <p>
              <strong className="text-accent-cyan">Astrophysical Phenomenon:</strong> All 8 confirmed planets of the Kepler-90 system orbit within <strong className="text-white">1.01 AU</strong> of their parent star. In other words, this entire 8-planet planetary system is packed into a space equivalent to Earth&apos;s distance from the Sun!
            </p>
          </div>

          <div className="space-y-3 pt-2">
            <div className="text-[11px] font-mono text-astro-muted flex justify-between">
              <span>Kepler-90 System (8 Planets within 1.01 AU)</span>
              <span className="text-accent-blue font-bold">1.01 AU Total Span</span>
            </div>
            <div className="h-4 w-full bg-space-950 rounded-full border border-space-border relative flex items-center px-1">
              {/* Star */}
              <div className="h-3 w-3 rounded-full bg-yellow-400 shrink-0 shadow-lg shadow-yellow-400/50" />
              {/* 8 planets marked along 1.01 AU */}
              {system?.planets.map((p) => {
                const pct = (p.semi_major_axis_au / 1.05) * 100;
                return (
                  <div
                    key={p.letter}
                    className="absolute -top-1 bottom-0 flex flex-col items-center group cursor-pointer"
                    style={{ left: `${Math.min(96, Math.max(4, pct))}%` }}
                    title={`${p.name}: ${p.semi_major_axis_au} AU`}
                  >
                    <div
                      className={`h-2.5 w-2.5 rounded-full ${p.discovered_by_ai ? "ring-2 ring-accent-emerald animate-pulse" : ""}`}
                      style={{ backgroundColor: p.color }}
                    />
                    <span className="text-[9px] font-mono text-astro-muted mt-5 group-hover:text-white">
                      {p.letter}
                    </span>
                  </div>
                );
              })}
            </div>
            <div className="flex justify-between text-[10px] font-mono text-astro-subtle pt-3">
              <span>Host Star (0.0 AU)</span>
              <span>Mercury Orbit (0.39 AU)</span>
              <span>Earth Orbit (1.00 AU) / Kepler-90h (1.01 AU)</span>
            </div>
          </div>
        </div>
      </div>

      {/* 8 Planets Catalog Cards */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-astro-text font-mono">
          All 8 Confirmed Planets of Kepler-90
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {system?.planets.map((p) => (
            <div
              key={p.letter}
              className={`rounded-xl border p-5 space-y-3 transition flex flex-col justify-between ${
                p.discovered_by_ai
                  ? "border-accent-emerald/60 bg-accent-emerald/5 shadow-lg shadow-accent-emerald/10"
                  : "border-space-border bg-space-850 hover:border-accent-blue/40"
              }`}
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className="h-3 w-3 rounded-full"
                      style={{ backgroundColor: p.color }}
                    />
                    <h4 className="font-bold text-astro-text font-mono">{p.name}</h4>
                  </div>
                  {p.discovered_by_ai && (
                    <span className="text-[9px] font-mono font-bold bg-accent-emerald/20 text-accent-emerald px-1.5 py-0.5 rounded">
                      AI DISCOVERY
                    </span>
                  )}
                </div>

                <div className="space-y-1.5 text-xs font-mono">
                  <div className="flex justify-between">
                    <span className="text-astro-muted">Period:</span>
                    <span className="text-astro-text">{p.period_days.toFixed(3)} days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-astro-muted">Semi-Major Axis:</span>
                    <span className="text-accent-blue">{p.semi_major_axis_au.toFixed(3)} AU</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-astro-muted">Radius:</span>
                    <span className="text-accent-cyan">{p.radius_earth.toFixed(2)} R⊕</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-astro-muted">Temp:</span>
                    <span className="text-accent-gold">{p.temp_kelvin} K</span>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-space-border/60 flex items-center justify-between text-xs font-mono">
                <span className="text-astro-subtle">Year: {p.discovery_year}</span>
                <Link
                  href={`/detector?kepid=11442793&period=${p.period_days}&duration=3.0&depth=${p.transit_depth_ppm}`}
                  className="text-accent-blue hover:text-white transition font-semibold"
                >
                  Test in Lab →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

