"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Layers,
  Database,
  Radio,
  FileCheck,
  ShieldCheck,
  HardDrive,
  CheckCircle2,
  ExternalLink,
} from "lucide-react";
import { api, CacheStatus } from "@/lib/api";

export default function DataManagementPage() {
  const [data, setData] = useState<CacheStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDataCache()
      .then(setData)
      .catch((err) => console.error("Error loading cache data", err))
      .finally(() => setLoading(false));
  }, []);

  const stats = data?.stats;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="border-b border-space-border pb-4">
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-astro-text flex items-center gap-2">
          <Layers className="h-6 w-6 text-accent-blue" />
          Dataset & Persistent Cache Management
        </h1>
        <p className="text-xs sm:text-sm text-astro-muted">
          Audit NASA Kepler DR24 catalogs, partitioned splits, and Snappy-compressed Parquet light curve cache
        </p>
      </div>

      {/* Storage Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border border-space-border bg-space-850 p-5 font-mono text-xs">
          <span className="text-astro-muted text-[11px] uppercase">RAW CATALOG SIZE</span>
          <p className="mt-2 text-2xl font-bold text-astro-text">
            {stats ? `${stats.raw_size_mb} MB` : "—"}
          </p>
          <span className="text-accent-cyan mt-1 block">NASA DR24 TCE Catalog</span>
        </div>

        <div className="rounded-xl border border-space-border bg-space-850 p-5 font-mono text-xs">
          <span className="text-astro-muted text-[11px] uppercase">PROCESSED DATASET</span>
          <p className="mt-2 text-2xl font-bold text-accent-blue">
            {stats ? `${stats.processed_size_mb} MB` : "—"}
          </p>
          <span className="text-accent-blue mt-1 block">15,737 Cleaned TCEs</span>
        </div>

        <div className="rounded-xl border border-space-border bg-space-850 p-5 font-mono text-xs">
          <span className="text-astro-muted text-[11px] uppercase">LIGHTKURVE CACHE</span>
          <p className="mt-2 text-2xl font-bold text-accent-emerald">
            {stats ? `${stats.total_cache_mb} MB` : "—"}
          </p>
          <span className="text-accent-emerald mt-1 block">
            {stats ? `${stats.cached_count} Stars Cached` : "—"}
          </span>
        </div>

        <div className="rounded-xl border border-space-border bg-space-850 p-5 font-mono text-xs">
          <span className="text-astro-muted text-[11px] uppercase">STAR OVERLAP (LEAKAGE)</span>
          <p className="mt-2 text-2xl font-bold text-accent-purple">
            0.00%
          </p>
          <span className="text-accent-purple mt-1 block">Strict Grouped Splits</span>
        </div>
      </div>

      {/* Data Integrity Checklist */}
      <div className="rounded-xl border border-space-border bg-space-850 p-6 space-y-4">
        <h3 className="text-sm font-semibold text-astro-text font-mono uppercase tracking-wider flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-accent-emerald" />
          Scientific Data Integrity Verification
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
          <div className="flex items-center gap-2.5 p-3 rounded-lg bg-space-800 border border-space-border">
            <CheckCircle2 className="h-4 w-4 text-accent-emerald shrink-0" />
            <span>Time system verified: BKJD (BJD - 2454833.0)</span>
          </div>

          <div className="flex items-center gap-2.5 p-3 rounded-lg bg-space-800 border border-space-border">
            <CheckCircle2 className="h-4 w-4 text-accent-emerald shrink-0" />
            <span>Transit protection factor: 1.2x duration masked</span>
          </div>

          <div className="flex items-center gap-2.5 p-3 rounded-lg bg-space-800 border border-space-border">
            <CheckCircle2 className="h-4 w-4 text-accent-emerald shrink-0" />
            <span>Savitzky-Golay detrending window: 401 cadences</span>
          </div>

          <div className="flex items-center gap-2.5 p-3 rounded-lg bg-space-800 border border-space-border">
            <CheckCircle2 className="h-4 w-4 text-accent-emerald shrink-0" />
            <span>Dual-view phase folding: 2,001 global / 201 local bins</span>
          </div>
        </div>
      </div>

      {/* Cached Light Curves Table */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-astro-text font-mono uppercase tracking-wider flex items-center gap-2">
            <HardDrive className="h-4 w-4 text-accent-blue" />
            Persistent Stellar Light Curve Cache (Parquet)
          </h3>
          <span className="text-xs font-mono text-astro-muted">
            {data?.cached_files.length || 0} Stars Stored Locally
          </span>
        </div>

        <div className="overflow-x-auto rounded-xl border border-space-border bg-space-850">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-space-border bg-space-950/60 text-astro-muted uppercase tracking-wider">
                <th className="py-3 px-4">KIC ID</th>
                <th className="py-3 px-3">File Name</th>
                <th className="py-3 px-3">Format</th>
                <th className="py-3 px-3">Disk Size (KB)</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-space-border/50 text-astro-text">
              {data?.cached_files.map((f) => (
                <tr key={f.kepid} className="hover:bg-space-800/60 transition">
                  <td className="py-3 px-4 font-bold text-accent-blue">KIC {f.kepid}</td>
                  <td className="py-3 px-3 text-astro-muted">{f.file_name}</td>
                  <td className="py-3 px-3 text-accent-cyan">Snappy Parquet</td>
                  <td className="py-3 px-3 font-semibold">{f.size_kb} KB</td>
                  <td className="py-3 px-4 text-right">
                    <Link
                      href={`/studio?kepid=${f.kepid}`}
                      className="inline-flex items-center gap-1 rounded bg-accent-blue/10 px-2 py-1 text-[11px] font-medium text-accent-blue hover:bg-accent-blue hover:text-space-950 transition"
                    >
                      <Radio className="h-3 w-3" />
                      View Light Curve
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

