"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  Radio,
  RotateCcw,
  Search,
} from "lucide-react";
import { api, LightCurveData, FoldedViews } from "@/lib/api";
import LightCurveChart from "@/components/LightCurveChart";

function StudioContent() {
  const searchParams = useSearchParams();
  const initialKepid = searchParams.get("kepid") ? Number(searchParams.get("kepid")) : 11442793;

  const [kepid, setKepid] = useState<number>(initialKepid);
  const [activeTab, setActiveTab] = useState<"detrended" | "raw" | "folded">("detrended");
  const [loading, setLoading] = useState<boolean>(true);
  const [lcData, setLcData] = useState<LightCurveData | null>(null);
  const [viewsData, setViewsData] = useState<FoldedViews | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchLightcurve = async (targetKepid: number) => {
    setLoading(true);
    setError(null);
    try {
      const [lc, views] = await Promise.all([
        api.getLightcurve(targetKepid, 3000),
        api.getFoldedViews(targetKepid, 1).catch(() => null),
      ]);
      setLcData(lc);
      setViewsData(views);
    } catch (err: any) {
      setError(err.message || "Failed to load light curve");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLightcurve(kepid);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchLightcurve(kepid);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-space-border pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-astro-text flex items-center gap-2">
            <Radio className="h-6 w-6 text-accent-blue" />
            Light Curve Analysis Studio
          </h1>
          <p className="text-xs sm:text-sm text-astro-muted">
            Inspect raw NASA Kepler photometric time series, Savitzky-Golay detrending, and phase-folded dual views
          </p>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="flex items-center gap-2">
          <div className="relative">
            <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-xs font-mono text-astro-subtle">
              KIC
            </span>
            <input
              type="number"
              value={kepid}
              onChange={(e) => setKepid(Number(e.target.value))}
              className="w-40 rounded-lg border border-space-border bg-space-850 pl-10 pr-3 py-2 text-xs font-mono text-astro-text focus:border-accent-blue focus:outline-none"
              placeholder="e.g. 11442793"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-accent-blue px-3 py-2 text-xs font-mono font-bold text-space-950 hover:bg-accent-blue/90 disabled:opacity-50 transition"
          >
            {loading ? <RotateCcw className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          </button>
        </form>
      </div>

      {/* Target Status Telemetry */}
      {lcData && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="rounded-xl border border-space-border bg-space-850 p-4 font-mono text-xs">
            <span className="text-astro-muted text-[11px] uppercase">TOTAL OBSERVATIONS</span>
            <p className="mt-1 text-lg font-bold text-astro-text">
              {lcData.total_points.toLocaleString()} Cadences
            </p>
          </div>
          <div className="rounded-xl border border-space-border bg-space-850 p-4 font-mono text-xs">
            <span className="text-astro-muted text-[11px] uppercase">DISPLAY RESOLUTION</span>
            <p className="mt-1 text-lg font-bold text-accent-blue">
              {lcData.returned_points.toLocaleString()} Points
            </p>
          </div>
          <div className="rounded-xl border border-space-border bg-space-850 p-4 font-mono text-xs">
            <span className="text-astro-muted text-[11px] uppercase">DATA STORAGE SOURCE</span>
            <p className="mt-1 text-lg font-bold text-accent-emerald uppercase">
              {lcData.source}
            </p>
          </div>
          <div className="rounded-xl border border-space-border bg-space-850 p-4 font-mono text-xs">
            <span className="text-astro-muted text-[11px] uppercase">FILTER WINDOW</span>
            <p className="mt-1 text-lg font-bold text-accent-purple">
              401 Cadences (S-G)
            </p>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="rounded-xl border border-accent-rose/50 bg-accent-rose/10 p-4 text-xs font-mono text-accent-rose">
          {error}
        </div>
      )}

      {/* View Switcher Tabs */}
      <div className="flex border-b border-space-border">
        <button
          onClick={() => setActiveTab("detrended")}
          className={`px-4 py-2 text-xs font-mono font-medium border-b-2 transition ${
            activeTab === "detrended"
              ? "border-accent-blue text-accent-blue"
              : "border-transparent text-astro-muted hover:text-white"
          }`}
        >
          Flattened & Detrended Flux
        </button>
        <button
          onClick={() => setActiveTab("raw")}
          className={`px-4 py-2 text-xs font-mono font-medium border-b-2 transition ${
            activeTab === "raw"
              ? "border-accent-blue text-accent-blue"
              : "border-transparent text-astro-muted hover:text-white"
          }`}
        >
          Raw Photometry & Stellar Trend
        </button>
        <button
          onClick={() => setActiveTab("folded")}
          className={`px-4 py-2 text-xs font-mono font-medium border-b-2 transition ${
            activeTab === "folded"
              ? "border-accent-blue text-accent-blue"
              : "border-transparent text-astro-muted hover:text-white"
          }`}
        >
          Phase-Folded Dual Views
        </button>
      </div>

      {/* Chart Panels */}
      {lcData && (
        <div className="space-y-6">
          {activeTab === "detrended" && (
            <LightCurveChart
              title={`Flattened Light Curve (KIC ${lcData.kepid}) · Outliers & Low-Frequency Stellar Variability Removed`}
              xData={lcData.time}
              yData={lcData.detrended_flux || lcData.raw_flux}
              xLabel="Time (BKJD = BJD - 2454833.0)"
              yLabel="Normalized Relative Flux"
              color="#35D49A"
              height={360}
            />
          )}

          {activeTab === "raw" && (
            <div className="space-y-4">
              <LightCurveChart
                title={`Raw Kepler Photometry (KIC ${lcData.kepid})`}
                xData={lcData.time}
                yData={lcData.raw_flux}
                xLabel="Time (BKJD)"
                yLabel="Raw Electron Flux (e⁻/s)"
                color="#63B3FF"
                height={320}
              />
              {lcData.trend_flux && (
                <LightCurveChart
                  title="Savitzky-Golay Low-Frequency Trend Model (Window = 401 cadences)"
                  xData={lcData.time}
                  yData={lcData.trend_flux}
                  xLabel="Time (BKJD)"
                  yLabel="Trend Level"
                  color="#FFBE55"
                  height={220}
                />
              )}
            </div>
          )}

          {activeTab === "folded" && viewsData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <LightCurveChart
                title={`Global Folded View (P = ${viewsData.period} d)`}
                xData={viewsData.global_phase}
                yData={viewsData.global_view}
                xLabel="Phase φ ∈ [-0.5, 0.5]"
                yLabel="Normalized Flux"
                color="#63B3FF"
                height={320}
              />
              <LightCurveChart
                title={`Local Transit View (Duration = ${viewsData.duration_hours} h)`}
                xData={viewsData.local_phase}
                yData={viewsData.local_view}
                xLabel="In-Transit Phase Window"
                yLabel="Normalized Flux"
                color="#8B7CFF"
                height={320}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function LightCurveStudioPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs font-mono text-astro-subtle">Loading Light Curve Studio...</div>}>
      <StudioContent />
    </Suspense>
  );
}

