"use client";

import { useEffect, useState } from "react";
import { History, RotateCcw, Filter, CheckCircle2, ChevronRight, Layers } from "lucide-react";
import { api, ExperimentRun } from "@/lib/api";

export default function ExperimentsPage() {
  const [runs, setRuns] = useState<ExperimentRun[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedRun, setSelectedRun] = useState<ExperimentRun | null>(null);

  useEffect(() => {
    api.getExperiments()
      .then((data) => {
        setRuns(data);
        if (data.length > 0) setSelectedRun(data[0]);
      })
      .catch((err) => console.error("Error loading experiments", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-space-border pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-astro-text flex items-center gap-2">
            <History className="h-6 w-6 text-accent-blue" />
            Experiment Tracking Center
          </h1>
          <p className="text-xs sm:text-sm text-astro-muted">
            SQLite-backed experiment registry for reproducibility and hyperparameter comparison
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono text-astro-muted">
          <span className="h-2 w-2 rounded-full bg-accent-emerald" />
          <span>SQLite Database: <code className="text-accent-cyan">experiments.db</code></span>
        </div>
      </div>

      {/* Main Runs Table */}
      <div className="overflow-x-auto rounded-xl border border-space-border bg-space-850">
        <table className="w-full text-left border-collapse text-xs font-mono">
          <thead>
            <tr className="border-b border-space-border bg-space-950/60 text-astro-muted uppercase tracking-wider">
              <th className="py-3 px-4">Run ID</th>
              <th className="py-3 px-3">Timestamp</th>
              <th className="py-3 px-3">Model Type</th>
              <th className="py-3 px-3">Duration (s)</th>
              <th className="py-3 px-3">Val AUC</th>
              <th className="py-3 px-3">Test AUC</th>
              <th className="py-3 px-3">Avg Precision</th>
              <th className="py-3 px-3">F1 Score</th>
              <th className="py-3 px-4 text-right">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-space-border/50 text-astro-text">
            {loading ? (
              <tr>
                <td colSpan={9} className="py-12 text-center text-astro-subtle">
                  Loading experiment runs from SQLite registry...
                </td>
              </tr>
            ) : runs.length === 0 ? (
              <tr>
                <td colSpan={9} className="py-12 text-center text-astro-subtle">
                  No recorded experiments found in registry.
                </td>
              </tr>
            ) : (
              runs.map((r) => {
                const isSelected = selectedRun?.experiment_id === r.experiment_id;
                return (
                  <tr
                    key={r.experiment_id}
                    onClick={() => setSelectedRun(r)}
                    className={`cursor-pointer transition ${
                      isSelected ? "bg-space-800" : "hover:bg-space-800/50"
                    }`}
                  >
                    <td className="py-3 px-4 font-bold text-accent-blue">{r.experiment_id}</td>
                    <td className="py-3 px-3 text-astro-muted">{r.timestamp?.replace("T", " ").slice(0, 19)}</td>
                    <td className="py-3 px-3 font-semibold text-accent-purple">{r.model_type}</td>
                    <td className="py-3 px-3">{r.training_duration ? r.training_duration.toFixed(1) : "—"}</td>
                    <td className="py-3 px-3 text-accent-emerald font-bold">
                      {r.best_val_auc ? r.best_val_auc.toFixed(4) : "—"}
                    </td>
                    <td className="py-3 px-3 text-accent-gold font-bold">
                      {r.test_auc ? r.test_auc.toFixed(4) : "—"}
                    </td>
                    <td className="py-3 px-3">{r.average_precision ? r.average_precision.toFixed(4) : "—"}</td>
                    <td className="py-3 px-3">{r.f1_score ? r.f1_score.toFixed(4) : "—"}</td>
                    <td className="py-3 px-4 text-right text-accent-blue">
                      <ChevronRight className="h-4 w-4 ml-auto" />
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Selected Experiment Inspector */}
      {selectedRun && (
        <div className="rounded-xl border border-space-border bg-space-850 p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-space-border pb-3">
            <h3 className="text-sm font-bold font-mono text-astro-text flex items-center gap-2">
              <Layers className="h-4 w-4 text-accent-blue" />
              Experiment Run Parameters & Metadata: {selectedRun.experiment_id}
            </h3>
            <span className="text-xs font-mono text-accent-cyan">
              Seed: {selectedRun.random_seed} · Dataset: {selectedRun.dataset_version}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Parameters JSON */}
            <div className="rounded-lg bg-space-900 border border-space-border p-4 font-mono text-xs space-y-2">
              <span className="text-[11px] text-astro-muted uppercase block">
                Hyperparameters & Configuration
              </span>
              <pre className="text-astro-text overflow-x-auto p-2 bg-space-950 rounded border border-space-border">
                {JSON.stringify(selectedRun.parameters || {}, null, 2)}
              </pre>
            </div>

            {/* Metrics JSON */}
            <div className="rounded-lg bg-space-900 border border-space-border p-4 font-mono text-xs space-y-2">
              <span className="text-[11px] text-astro-muted uppercase block">
                Recorded Evaluation Metrics
              </span>
              <pre className="text-astro-text overflow-x-auto p-2 bg-space-950 rounded border border-space-border">
                {JSON.stringify(selectedRun.metrics || {}, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

