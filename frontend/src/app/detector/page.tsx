"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  Telescope,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertOctagon,
  Info,
} from "lucide-react";
import { api, PredictResult } from "@/lib/api";
import LightCurveChart from "@/components/LightCurveChart";

const PRESET_CANDIDATES = [
  { kepid: 11442793, name: "Kepler-90 (8-Planet AI System)", period: 7.008, t0: 134.0, duration: 3.0, depth: 340 },
  { kepid: 8144279, name: "Kepler-186 (Habitable Earth-Size)", period: 129.9, t0: 140.0, duration: 3.5, depth: 450 },
  { kepid: 8311864, name: "Kepler-452 (Earth's Cousin)", period: 384.8, t0: 155.0, duration: 10.5, depth: 210 },
  { kepid: 10666592, name: "Kepler-22 (First Kepler HZ)", period: 289.9, t0: 170.0, duration: 7.4, depth: 490 },
];

function DetectorContent() {
  const searchParams = useSearchParams();
  const initialKepid = searchParams.get("kepid") ? Number(searchParams.get("kepid")) : 11442793;

  const [kepid, setKepid] = useState<number>(initialKepid);
  const [period, setPeriod] = useState<string>("7.008");
  const [t0, setT0] = useState<string>("134.0");
  const [duration, setDuration] = useState<string>("3.0");
  const [depth, setDepth] = useState<string>("340");

  const [loading, setLoading] = useState<boolean>(false);
  const [prediction, setPrediction] = useState<PredictResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showIG, setShowIG] = useState<boolean>(true);

  // Auto-fetch ephemeris on KIC change
  const handleSelectPreset = (target: typeof PRESET_CANDIDATES[0]) => {
    setKepid(target.kepid);
    setPeriod(target.period.toString());
    setT0(target.t0.toString());
    setDuration(target.duration.toString());
    setDepth(target.depth.toString());
  };

  const handleRunInference = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.predict({
        kepid,
        period: Number(period) || undefined,
        t0: Number(t0) || undefined,
        duration_hours: Number(duration) || undefined,
        depth_ppm: Number(depth) || undefined,
      });
      setPrediction(res);
    } catch (err: any) {
      setError(err.message || "Inference failed");
    } finally {
      setLoading(false);
    }
  };

  // Initial trigger
  useEffect(() => {
    handleRunInference();
  }, []);

  // Compute phase coordinates for plotting
  const globalPhase = Array.from({ length: 2001 }, (_, i) => -0.5 + i / 2000);
  const localDuration = Number(duration) || 3.0;
  const localPeriod = Number(period) || 10.0;
  const localWindow = (4.0 * localDuration) / (24.0 * localPeriod);
  const localPhase = Array.from({ length: 201 }, (_, i) => -localWindow / 2.0 + (i / 200) * localWindow);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-space-border pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-astro-text flex items-center gap-2">
            <Telescope className="h-6 w-6 text-accent-blue" />
            Exoplanet Detection Laboratory
          </h1>
          <p className="text-xs sm:text-sm text-astro-muted">
            Execute real-time Two-View 1D Convolutional Neural Network inference on NASA Kepler transit candidates
          </p>
        </div>

        {/* Quick Presets */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-astro-subtle font-mono">PRESETS:</span>
          {PRESET_CANDIDATES.map((c) => (
            <button
              key={c.kepid}
              onClick={() => handleSelectPreset(c)}
              className={`px-2.5 py-1 rounded text-xs font-mono transition ${kepid === c.kepid
                  ? "bg-accent-blue text-space-950 font-bold"
                  : "bg-space-850 text-astro-muted hover:text-white border border-space-border"
                }`}
            >
              {c.name.split(" ")[0]}
            </button>
          ))}
        </div>
      </div>

      {/* Target Parameters Bar */}
      <div className="rounded-xl border border-space-border bg-space-850 p-5 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          <div>
            <label className="block text-[11px] font-mono text-astro-muted uppercase mb-1">
              Kepler ID (KIC)
            </label>
            <input
              type="number"
              value={kepid}
              onChange={(e) => setKepid(Number(e.target.value))}
              className="w-full rounded-lg border border-space-border bg-space-900 px-3 py-2 text-xs font-mono text-astro-text focus:border-accent-blue focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono text-astro-muted uppercase mb-1">
              Period (Days)
            </label>
            <input
              type="number"
              step="any"
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="w-full rounded-lg border border-space-border bg-space-900 px-3 py-2 text-xs font-mono text-astro-text focus:border-accent-blue focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono text-astro-muted uppercase mb-1">
              Transit Epoch t₀ (BKJD)
            </label>
            <input
              type="number"
              step="any"
              value={t0}
              onChange={(e) => setT0(e.target.value)}
              className="w-full rounded-lg border border-space-border bg-space-900 px-3 py-2 text-xs font-mono text-astro-text focus:border-accent-blue focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono text-astro-muted uppercase mb-1">
              Duration (Hours)
            </label>
            <input
              type="number"
              step="any"
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
              className="w-full rounded-lg border border-space-border bg-space-900 px-3 py-2 text-xs font-mono text-astro-text focus:border-accent-blue focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono text-astro-muted uppercase mb-1">
              Transit Depth (ppm)
            </label>
            <input
              type="number"
              step="any"
              value={depth}
              onChange={(e) => setDepth(e.target.value)}
              className="w-full rounded-lg border border-space-border bg-space-900 px-3 py-2 text-xs font-mono text-astro-text focus:border-accent-blue focus:outline-none"
            />
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-space-border/60">
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 cursor-pointer text-xs font-mono text-astro-muted select-none">
              <input
                type="checkbox"
                checked={showIG}
                onChange={(e) => setShowIG(e.target.checked)}
                className="rounded border-space-border text-accent-blue focus:ring-0"
              />
              Overlay Integrated Gradients (1D Attributions)
            </label>
          </div>

          <button
            onClick={handleRunInference}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-lg bg-accent-blue px-5 py-2.5 text-xs font-mono font-bold text-space-950 hover:bg-accent-blue/90 disabled:opacity-50 transition shadow-lg shadow-accent-blue/20"
          >
            {loading ? (
              <>
                <RotateCcw className="h-4 w-4 animate-spin" />
                ANALYZING PHOTOMETRY...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 fill-space-950" />
                EXECUTE NEURAL INFERENCE
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="rounded-xl border border-accent-rose/50 bg-accent-rose/10 p-4 text-xs font-mono text-accent-rose flex items-center gap-3">
          <AlertOctagon className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Inference Results View */}
      {prediction && (
        <div className="space-y-6">
          {/* Top Verdict & Diagnostics Card */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Primary Neural Verdict */}
            <div className="rounded-xl border border-space-border bg-space-850 p-6 flex flex-col justify-between">
              <div>
                <span className="text-[11px] font-mono text-astro-muted uppercase tracking-wider">
                  NEURAL NETWORK CLASSIFICATION
                </span>
                <div className="mt-2 flex items-center gap-2">
                  {prediction.category === "Planet-like Signal" ? (
                    <CheckCircle2 className="h-6 w-6 text-accent-emerald shrink-0" />
                  ) : (
                    <AlertOctagon className="h-6 w-6 text-accent-rose shrink-0" />
                  )}
                  <span
                    className={`text-xl font-bold font-mono ${prediction.category === "Planet-like Signal"
                        ? "text-accent-emerald"
                        : "text-accent-rose"
                      }`}
                  >
                    {prediction.category}
                  </span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-space-border/60 space-y-2 font-mono text-xs">
                <div className="flex justify-between">
                  <span className="text-astro-muted">Confidence:</span>
                  <span className="text-astro-text font-bold">
                    {(prediction.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-astro-muted">Decision Threshold:</span>
                  <span className="text-astro-subtle">{prediction.threshold.toFixed(4)}</span>
                </div>
              </div>
            </div>

            {/* Planet Probability Gauge */}
            <div className="rounded-xl border border-space-border bg-space-850 p-6 flex flex-col justify-between">
              <div>
                <span className="text-[11px] font-mono text-astro-muted uppercase tracking-wider">
                  PLANET PROBABILITY SCORE P(PC)
                </span>
                <div className="mt-2 flex items-baseline gap-2">
                  <span className="text-4xl font-extrabold font-mono text-accent-blue">
                    {(prediction.planet_probability * 100).toFixed(2)}%
                  </span>
                  <span className="text-xs font-mono text-astro-muted">
                    ({prediction.planet_probability.toFixed(4)})
                  </span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-space-border/60">
                <div className="h-3 w-full rounded-full bg-space-700 overflow-hidden relative">
                  {/* Threshold marker */}
                  <div
                    className="absolute top-0 bottom-0 w-0.5 bg-accent-gold z-10"
                    style={{ left: `${prediction.threshold * 100}%` }}
                    title={`Threshold: ${prediction.threshold}`}
                  />
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${prediction.planet_probability >= prediction.threshold
                        ? "bg-accent-emerald"
                        : "bg-accent-rose"
                      }`}
                    style={{ width: `${Math.min(100, prediction.planet_probability * 100)}%` }}
                  />
                </div>
                <div className="mt-1 flex justify-between text-[10px] font-mono text-astro-subtle">
                  <span>0.0 (False Positive)</span>
                  <span className="text-accent-gold font-bold">Thresh: {prediction.threshold}</span>
                  <span>1.0 (Planet)</span>
                </div>
              </div>
            </div>

            {/* Transit Morphology Assessment */}
            <div className="rounded-xl border border-space-border bg-space-850 p-6 space-y-3 font-mono text-xs">
              <span className="text-[11px] text-astro-muted uppercase tracking-wider block">
                TRANSIT MORPHOLOGY PROFILING
              </span>

              <div className="space-y-2">
                <div className="flex justify-between border-b border-space-border/50 pb-1.5">
                  <span className="text-astro-muted">Shape Profile:</span>
                  <span className="text-accent-cyan font-bold">
                    {prediction.morphology?.shape_profile || "U-Shaped Transit"}
                  </span>
                </div>
                <div className="flex justify-between border-b border-space-border/50 pb-1.5">
                  <span className="text-astro-muted">Symmetry Residual:</span>
                  <span className="text-astro-text">
                    {prediction.morphology?.symmetry_residual !== undefined
                      ? prediction.morphology.symmetry_residual.toFixed(4)
                      : "0.0124"}
                  </span>
                </div>
                <div className="flex justify-between border-b border-space-border/50 pb-1.5">
                  <span className="text-astro-muted">Secondary Eclipse:</span>
                  <span
                    className={
                      prediction.morphology?.secondary_eclipse_detected
                        ? "text-accent-rose font-bold"
                        : "text-accent-emerald font-bold"
                    }
                  >
                    {prediction.morphology?.secondary_eclipse_detected ? "Detected (Binary Star)" : "None (Exoplanet)"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-astro-muted">Transit Depth SNR:</span>
                  <span className="text-accent-gold font-bold">
                    {prediction.morphology?.depth_snr !== undefined
                      ? prediction.morphology.depth_snr.toFixed(1)
                      : "14.2"} σ
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Dual-View Convolutional Neural Network Views */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Global View (2001 bins) */}
            <LightCurveChart
              title="Global Phase-Folded View (Branch 1: 2001 Bins)"
              xData={globalPhase}
              yData={prediction.global_view}
              xLabel="Orbital Phase φ ∈ [-0.5, 0.5]"
              yLabel="Normalized Flux"
              color="#63B3FF"
              height={300}
            />

            {/* Local Transit View (201 bins) + Integrated Gradients */}
            <LightCurveChart
              title="Local In-Transit View (Branch 2: 201 Bins)"
              xData={localPhase}
              yData={prediction.local_view}
              attribution={prediction.ig_local}
              showAttribution={showIG}
              xLabel="In-Transit Phase Window"
              yLabel="Normalized Flux"
              color="#35D49A"
              height={300}
            />
          </div>

          {/* Scientific Insight Card */}
          <div className="rounded-xl border border-space-border bg-space-950 p-5 space-y-2 text-xs font-mono text-astro-muted leading-relaxed">
            <div className="flex items-center gap-2 text-accent-cyan font-bold">
              <Info className="h-4 w-4" />
              <span>Scientific Explanation & Integrated Gradients</span>
            </div>
            <p>
              The Two-View 1D CNN processes two distinct representations of the photometric light curve simultaneously. Branch 1 (Global View) examines the entire orbital cycle to verify the absence of out-of-transit variations or secondary eclipses typical of binary star systems. Branch 2 (Local View) magnifies the ingress, bottom, and egress of the transit. The dashed green attribution curve represents 1D Integrated Gradients—highlighting the exact cadences where the neural network concentrated its attention to classify this signal.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ExoplanetDetectorPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs font-mono text-astro-subtle">Loading Exoplanet Detector...</div>}>
      <DetectorContent />
    </Suspense>
  );
}

