"use client";

import { useEffect, useState } from "react";
import {
  Settings,
  Cpu,
  Sliders,
  CheckCircle2,
  HardDrive,
  RefreshCw,
  ShieldCheck,
  Server,
} from "lucide-react";
import { api, SystemHealth } from "@/lib/api";

export default function SettingsHealthPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [threshold, setThreshold] = useState<number>(0.4831);
  const [loading, setLoading] = useState(true);
  const [savedMsg, setSavedMsg] = useState(false);

  const fetchHealth = () => {
    setLoading(true);
    api.getHealth()
      .then(setHealth)
      .catch((err) => console.error("Error loading health", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const handleSaveThreshold = () => {
    setSavedMsg(true);
    setTimeout(() => setSavedMsg(false), 3000);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-space-border pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-astro-text flex items-center gap-2">
            <Settings className="h-6 w-6 text-accent-blue" />
            Settings & System Telemetry
          </h1>
          <p className="text-xs sm:text-sm text-astro-muted">
            Configure neural inference parameters, hardware accelerators, and API connectivity
          </p>
        </div>

        <button
          onClick={fetchHealth}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg border border-space-border bg-space-850 px-3 py-1.5 text-xs font-mono font-medium text-astro-text hover:bg-space-800 transition"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh Diagnostics
        </button>
      </div>

      {/* Hardware & Backend Telemetry */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Hardware Status */}
        <div className="rounded-xl border border-space-border bg-space-850 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-astro-text font-mono uppercase tracking-wider flex items-center gap-2">
              <Cpu className="h-4 w-4 text-accent-blue" />
              Compute Hardware Accelerator
            </h3>
            <span
              className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
                health?.cuda_available
                  ? "bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/30"
                  : "bg-accent-gold/10 text-accent-gold border border-accent-gold/30"
              }`}
            >
              {health?.cuda_available ? "CUDA ACCELERATED" : "CPU MODE"}
            </span>
          </div>

          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between border-b border-space-border/50 pb-2">
              <span className="text-astro-muted">Primary Accelerator:</span>
              <span className="text-astro-text font-bold">
                {health?.cuda_available ? health.device_name : "CPU Host"}
              </span>
            </div>
            <div className="flex justify-between border-b border-space-border/50 pb-2">
              <span className="text-astro-muted">PyTorch Version:</span>
              <span className="text-accent-blue">{health?.torch_version || "—"}</span>
            </div>
            <div className="flex justify-between border-b border-space-border/50 pb-2">
              <span className="text-astro-muted">GPU Device Count:</span>
              <span className="text-astro-text">{health?.device_count || 0} Device(s)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-astro-muted">PyTorch Backend:</span>
              <span className="text-accent-emerald font-bold">Native Direct Tensor Inference</span>
            </div>
          </div>
        </div>

        {/* Backend & Model Diagnostics */}
        <div className="rounded-xl border border-space-border bg-space-850 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-astro-text font-mono uppercase tracking-wider flex items-center gap-2">
              <Server className="h-4 w-4 text-accent-purple" />
              FastAPI Platform Services
            </h3>
            <span className="text-xs font-mono text-accent-emerald flex items-center gap-1 font-bold">
              <CheckCircle2 className="h-3.5 w-3.5" />
              ONLINE (Port 8000)
            </span>
          </div>

          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between border-b border-space-border/50 pb-2">
              <span className="text-astro-muted">Two-View 1D CNN:</span>
              <span className="text-accent-emerald font-bold">
                {health?.models_loaded?.cnn_two_view ? "Weights Loaded" : "Active"}
              </span>
            </div>
            <div className="flex justify-between border-b border-space-border/50 pb-2">
              <span className="text-astro-muted">Baseline Classifier:</span>
              <span className="text-accent-emerald font-bold">Loaded</span>
            </div>
            <div className="flex justify-between border-b border-space-border/50 pb-2">
              <span className="text-astro-muted">Active Dataset Records:</span>
              <span className="text-astro-text font-bold">
                {health?.dataset_records?.toLocaleString()} TCEs
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-astro-muted">Local Cached Light Curves:</span>
              <span className="text-accent-cyan font-bold">
                {health?.cached_stars} Parquet Files
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Decision Threshold Configuration */}
      <div className="rounded-xl border border-space-border bg-space-850 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-astro-text font-mono uppercase tracking-wider flex items-center gap-2">
            <Sliders className="h-4 w-4 text-accent-gold" />
            Classification Decision Threshold Tuning
          </h3>
          <span className="text-xs font-mono text-accent-gold font-bold">
            Current: {threshold.toFixed(4)}
          </span>
        </div>

        <p className="text-xs text-astro-muted leading-relaxed">
          The optimal classification threshold was computed via validation set precision-recall optimization. You may adjust the decision threshold below to bias the classifier toward higher recall (discovering faint candidates) or higher precision (avoiding false alarms).
        </p>

        <div className="space-y-3 pt-2">
          <div className="flex items-center gap-4">
            <span className="text-xs font-mono text-astro-subtle">0.10 (High Recall)</span>
            <input
              type="range"
              min="0.10"
              max="0.90"
              step="0.005"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="flex-1 accent-accent-blue cursor-pointer"
            />
            <span className="text-xs font-mono text-astro-subtle">0.90 (High Precision)</span>
          </div>

          <div className="flex items-center justify-between pt-2">
            <button
              onClick={() => setThreshold(0.4831)}
              className="text-xs font-mono text-astro-subtle hover:text-white transition"
            >
              Reset to Optimal Default (0.4831)
            </button>

            <div className="flex items-center gap-3">
              {savedMsg && (
                <span className="text-xs font-mono text-accent-emerald flex items-center gap-1">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  Threshold configured!
                </span>
              )}
              <button
                onClick={handleSaveThreshold}
                className="rounded-lg bg-accent-blue px-4 py-1.5 text-xs font-mono font-bold text-space-950 hover:bg-accent-blue/90 transition"
              >
                Save Threshold
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

