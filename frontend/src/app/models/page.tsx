"use client";

import { useEffect, useState } from "react";
import {
  Cpu,
  TrendingUp,
  Activity,
  Layers,
  ShieldCheck,
  Zap,
  BarChart2,
  GitBranch,
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import { api, ModelComparison } from "@/lib/api";

export default function ModelIntelligencePage() {
  const [data, setData] = useState<ModelComparison | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getModelComparison()
      .then(setData)
      .catch((err) => console.error("Error loading model comparison", err))
      .finally(() => setLoading(false));
  }, []);

  // Format ROC curve for Recharts
  const rocChartData = (data?.curves?.baseline?.roc?.x || []).map((fpr, i) => ({
    fpr: Number(fpr.toFixed(4)),
    baselineTPR: Number(data?.curves?.baseline?.roc?.y[i]?.toFixed(4) || 0),
    randomLine: Number(fpr.toFixed(4)),
  }));

  // Format PR curve for Recharts
  const prChartData = (data?.curves?.baseline?.pr?.x || []).map((recall, i) => ({
    recall: Number(recall.toFixed(4)),
    baselinePrecision: Number(data?.curves?.baseline?.pr?.y[i]?.toFixed(4) || 0),
  }));

  // Format Training History
  const historyData = (data?.training_history?.epoch || []).map((ep, i) => ({
    epoch: ep,
    trainLoss: Number(data?.training_history?.train_loss[i]?.toFixed(4) || 0),
    valLoss: Number(data?.training_history?.val_loss[i]?.toFixed(4) || 0),
    trainAuc: Number(data?.training_history?.train_auc[i]?.toFixed(4) || 0),
    valAuc: Number(data?.training_history?.val_auc[i]?.toFixed(4) || 0),
  }));

  const baseMetrics = data?.baseline_metrics || {};
  const cnnMetrics = data?.cnn_metrics || {};

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="border-b border-space-border pb-4">
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-astro-text flex items-center gap-2">
          <Cpu className="h-6 w-6 text-accent-blue" />
          Model Intelligence & Scientific Evaluation Center
        </h1>
        <p className="text-xs sm:text-sm text-astro-muted">
          Rigorous benchmarking: Baseline HistGradientBoosting vs PyTorch Two-View 1D Convolutional Neural Network
        </p>
      </div>

      {/* Model Benchmark Side-by-Side Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Baseline Model */}
        <div className="rounded-xl border border-space-border bg-space-850 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-[10px] font-mono uppercase bg-accent-gold/10 text-accent-gold px-2 py-0.5 rounded border border-accent-gold/30">
                ASTRONOMICAL TABULAR BASELINE
              </span>
              <h3 className="mt-2 text-lg font-bold text-astro-text">
                HistGradientBoostingClassifier
              </h3>
            </div>
            <div className="text-right">
              <span className="text-2xl font-extrabold font-mono text-accent-gold">
                0.9457
              </span>
              <p className="text-[10px] font-mono text-astro-muted">TEST ROC-AUC</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 font-mono text-xs">
            <div className="p-2.5 rounded bg-space-800 border border-space-border text-center">
              <span className="text-astro-subtle text-[10px] block">AVG PRECISION</span>
              <span className="font-bold text-accent-cyan">0.7836</span>
            </div>
            <div className="p-2.5 rounded bg-space-800 border border-space-border text-center">
              <span className="text-astro-subtle text-[10px] block">F1 SCORE</span>
              <span className="font-bold text-accent-emerald">0.7882</span>
            </div>
            <div className="p-2.5 rounded bg-space-800 border border-space-border text-center">
              <span className="text-astro-subtle text-[10px] block">RECALL</span>
              <span className="font-bold text-accent-blue">0.8846</span>
            </div>
          </div>

          {/* Baseline Confusion Matrix */}
          <div className="rounded-lg bg-space-900 border border-space-border p-3 space-y-2">
            <span className="text-[11px] font-mono text-astro-muted uppercase block">
              Test Split Confusion Matrix (1,594 TCEs)
            </span>
            <div className="grid grid-cols-2 gap-2 text-center font-mono text-xs">
              <div className="p-2 rounded bg-space-800 border border-space-border">
                <span className="text-[10px] text-astro-subtle block">TRUE NEGATIVE</span>
                <span className="font-bold text-astro-text">1,099 (AFP/NTP)</span>
              </div>
              <div className="p-2 rounded bg-space-800 border border-space-border">
                <span className="text-[10px] text-accent-rose block">FALSE POSITIVE</span>
                <span className="font-bold text-accent-rose">131</span>
              </div>
              <div className="p-2 rounded bg-space-800 border border-space-border">
                <span className="text-[10px] text-accent-rose block">FALSE NEGATIVE</span>
                <span className="font-bold text-accent-rose">42</span>
              </div>
              <div className="p-2 rounded bg-space-800 border border-space-border">
                <span className="text-[10px] text-accent-emerald block">TRUE POSITIVE</span>
                <span className="font-bold text-accent-emerald">322 (Planets)</span>
              </div>
            </div>
          </div>
        </div>

        {/* PyTorch Two-View CNN */}
        <div className="rounded-xl border border-space-border bg-space-850 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-[10px] font-mono uppercase bg-accent-blue/10 text-accent-blue px-2 py-0.5 rounded border border-accent-blue/30">
                DEEP LEARNING NEURAL PIPELINE
              </span>
              <h3 className="mt-2 text-lg font-bold text-astro-text">
                Two-View 1D Convolutional Neural Network
              </h3>
            </div>
            <div className="text-right">
              <span className="text-xs font-mono bg-accent-purple/20 text-accent-purple px-2 py-1 rounded">
                PyTorch 2.6 CUDA
              </span>
              <p className="text-[10px] font-mono text-astro-muted mt-1">Shallue & Vanderburg (2018)</p>
            </div>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex items-center justify-between p-2 rounded bg-space-800 border border-space-border">
              <span className="text-astro-muted">Branch 1 (Global View):</span>
              <span className="text-accent-blue font-bold">2,001 Photometric Bins</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-space-800 border border-space-border">
              <span className="text-astro-muted">Branch 2 (Local View):</span>
              <span className="text-accent-emerald font-bold">201 In-Transit Bins</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-space-800 border border-space-border">
              <span className="text-astro-muted">Dense Fusion:</span>
              <span className="text-accent-purple font-bold">Concat (1,024) → Linear 256 → 64 → 1</span>
            </div>
          </div>

          <div className="rounded-lg bg-space-900 border border-space-border p-3 text-xs text-astro-muted leading-relaxed">
            <span className="text-accent-blue font-bold">Architecture Advantage:</span> The dual-view network bypasses manual feature engineering. It directly observes raw transit geometry, preserving minuscule secondary dips and stellar limb-darkening signatures.
          </div>
        </div>
      </div>

      {/* Interactive Evaluation Curves */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ROC Curves */}
        <div className="rounded-xl border border-space-border bg-space-850 p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-mono font-bold text-astro-text uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-accent-gold" />
              Receiver Operating Characteristic (ROC Curve)
            </h4>
            <span className="text-xs font-mono text-accent-gold">AUC = 0.9457</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={rocChartData} margin={{ top: 10, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E2D4A" />
                <XAxis dataKey="fpr" stroke="#627591" tick={{ fill: "#627591", fontSize: 10, fontFamily: "monospace" }} />
                <YAxis domain={[0, 1]} stroke="#627591" tick={{ fill: "#627591", fontSize: 10, fontFamily: "monospace" }} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0D1424", borderColor: "#1E2D4A", fontSize: "11px", fontFamily: "monospace" }}
                />
                <Legend wrapperStyle={{ fontSize: "11px", fontFamily: "monospace" }} />
                <Line type="monotone" dataKey="baselineTPR" name="Baseline (AUC=0.9457)" stroke="#FFBE55" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="randomLine" name="Random Guess (AUC=0.5)" stroke="#627591" strokeDasharray="4 4" strokeWidth={1} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] font-mono text-astro-subtle">
            False Positive Rate (FPR) vs True Positive Rate (TPR) on holdout test set.
          </p>
        </div>

        {/* Precision-Recall Curves */}
        <div className="rounded-xl border border-space-border bg-space-850 p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-mono font-bold text-astro-text uppercase tracking-wider flex items-center gap-2">
              <BarChart2 className="h-4 w-4 text-accent-cyan" />
              Precision-Recall Curve (PR Curve)
            </h4>
            <span className="text-xs font-mono text-accent-cyan">Avg Precision = 0.7836</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={prChartData} margin={{ top: 10, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E2D4A" />
                <XAxis dataKey="recall" stroke="#627591" tick={{ fill: "#627591", fontSize: 10, fontFamily: "monospace" }} />
                <YAxis domain={[0, 1]} stroke="#627591" tick={{ fill: "#627591", fontSize: 10, fontFamily: "monospace" }} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0D1424", borderColor: "#1E2D4A", fontSize: "11px", fontFamily: "monospace" }}
                />
                <Legend wrapperStyle={{ fontSize: "11px", fontFamily: "monospace" }} />
                <Line type="monotone" dataKey="baselinePrecision" name="Baseline (AP=0.7836)" stroke="#38D9A9" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] font-mono text-astro-subtle">
            Recall vs Precision under class imbalance (22.9% positive class).
          </p>
        </div>
      </div>

      {/* PyTorch Neural Training History */}
      {historyData.length > 0 && (
        <div className="rounded-xl border border-space-border bg-space-850 p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-mono font-bold text-astro-text uppercase tracking-wider flex items-center gap-2">
              <Activity className="h-4 w-4 text-accent-purple" />
              PyTorch Two-View CNN Training & Validation History (GPU Run)
            </h4>
            <span className="text-xs font-mono text-accent-purple">13 Epochs (Early Stopping)</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={historyData} margin={{ top: 10, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E2D4A" />
                <XAxis dataKey="epoch" stroke="#627591" tick={{ fill: "#627591", fontSize: 10, fontFamily: "monospace" }} />
                <YAxis stroke="#627591" tick={{ fill: "#627591", fontSize: 10, fontFamily: "monospace" }} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0D1424", borderColor: "#1E2D4A", fontSize: "11px", fontFamily: "monospace" }}
                />
                <Legend wrapperStyle={{ fontSize: "11px", fontFamily: "monospace" }} />
                <Line type="monotone" dataKey="trainLoss" name="Training Loss" stroke="#FF657A" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="valLoss" name="Validation Loss" stroke="#35D49A" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}

