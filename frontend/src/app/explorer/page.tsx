"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Database,
  Search,
  Filter,
  ArrowUpDown,
  Download,
  ChevronLeft,
  ChevronRight,
  Telescope,
  Radio,
  ExternalLink,
} from "lucide-react";
import { api, Candidate } from "@/lib/api";

export default function CandidateExplorerPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(20);
  const [totalPages, setTotalPages] = useState<number>(1);

  // Filters
  const [searchKepid, setSearchKepid] = useState<string>("");
  const [disposition, setDisposition] = useState<string>("ALL");
  const [minPeriod, setMinPeriod] = useState<string>("");
  const [maxPeriod, setMaxPeriod] = useState<string>("");
  const [minSnr, setMinSnr] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("kepid");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const [loading, setLoading] = useState<boolean>(true);

  const fetchCandidates = async () => {
    setLoading(true);
    try {
      const res = await api.getCandidates({
        page,
        page_size: pageSize,
        kepid: searchKepid ? Number(searchKepid) : undefined,
        disposition: disposition !== "ALL" ? disposition : undefined,
        min_period: minPeriod ? Number(minPeriod) : undefined,
        max_period: maxPeriod ? Number(maxPeriod) : undefined,
        min_snr: minSnr ? Number(minSnr) : undefined,
        sort_by: sortBy,
        sort_dir: sortDir,
      });
      setCandidates(res.candidates);
      setTotal(res.total);
      setTotalPages(res.total_pages);
    } catch (err) {
      console.error("Failed to load candidates", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, [page, pageSize, disposition, sortBy, sortDir]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchCandidates();
  };

  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortBy(column);
      setSortDir("asc");
    }
    setPage(1);
  };

  const handleExportCSV = () => {
    if (candidates.length === 0) return;
    const headers = ["KIC ID", "Planet Num", "Period (days)", "Duration (hours)", "Depth (ppm)", "SNR", "Radius (R_earth)", "Disposition"];
    const rows = candidates.map((c) => [
      c.kepid,
      c.tce_plnt_num,
      c.tce_period ?? "",
      c.tce_duration ?? "",
      c.tce_depth ?? "",
      c.tce_model_snr ?? "",
      c.tce_prad ?? "",
      c.av_training_set ?? "",
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `kepler_dr24_candidates_page_${page}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-space-border pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-astro-text flex items-center gap-2">
            <Database className="h-6 w-6 text-accent-blue" />
            NASA Kepler DR24 Candidate Explorer
          </h1>
          <p className="text-xs sm:text-sm text-astro-muted">
            Search, filter, and inspect all 15,737 Kepler Transit Crossing Events
          </p>
        </div>

        <button
          onClick={handleExportCSV}
          className="inline-flex items-center gap-2 rounded-lg border border-space-border bg-space-850 px-3 py-2 text-xs font-mono font-medium text-astro-text hover:bg-space-800 transition"
        >
          <Download className="h-4 w-4 text-accent-blue" />
          Export Page CSV
        </button>
      </div>

      {/* Filter Toolbar */}
      <form onSubmit={handleSearchSubmit} className="rounded-xl border border-space-border bg-space-850 p-4 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          <div>
            <label className="block text-[11px] font-mono text-astro-muted uppercase mb-1">
              Search KIC ID
            </label>
            <input
              type="number"
              placeholder="e.g. 11442793"
              value={searchKepid}
              onChange={(e) => setSearchKepid(e.target.value)}
              className="w-full rounded-lg border border-space-border bg-space-900 px-3 py-1.5 text-xs font-mono text-astro-text focus:border-accent-blue focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono text-astro-muted uppercase mb-1">
              Disposition
            </label>
            <select
              value={disposition}
              onChange={(e) => {
                setDisposition(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-lg border border-space-border bg-space-900 px-3 py-1.5 text-xs font-mono text-astro-text focus:border-accent-blue focus:outline-none"
            >
              <option value="ALL">ALL (15,737)</option>
              <option value="PC">Planet Candidates (PC - 3,600)</option>
              <option value="AFP">Astrophysical False Positives (AFP - 9,596)</option>
              <option value="NTP">Non-Transiting Phenomenon (NTP - 2,541)</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-mono text-astro-muted uppercase mb-1">
              Min Period (days)
            </label>
            <input
              type="number"
              step="any"
              placeholder="0.5"
              value={minPeriod}
              onChange={(e) => setMinPeriod(e.target.value)}
              className="w-full rounded-lg border border-space-border bg-space-900 px-3 py-1.5 text-xs font-mono text-astro-text focus:border-accent-blue focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono text-astro-muted uppercase mb-1">
              Max Period (days)
            </label>
            <input
              type="number"
              step="any"
              placeholder="500"
              value={maxPeriod}
              onChange={(e) => setMaxPeriod(e.target.value)}
              className="w-full rounded-lg border border-space-border bg-space-900 px-3 py-1.5 text-xs font-mono text-astro-text focus:border-accent-blue focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono text-astro-muted uppercase mb-1">
              Min SNR
            </label>
            <input
              type="number"
              step="any"
              placeholder="7.1"
              value={minSnr}
              onChange={(e) => setMinSnr(e.target.value)}
              className="w-full rounded-lg border border-space-border bg-space-900 px-3 py-1.5 text-xs font-mono text-astro-text focus:border-accent-blue focus:outline-none"
            />
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-space-border/60">
          <span className="text-xs font-mono text-astro-muted">
            Found <strong className="text-astro-text">{total.toLocaleString()}</strong> matching candidate signals
          </span>
          <button
            type="submit"
            className="rounded-lg bg-accent-blue px-4 py-1.5 text-xs font-mono font-bold text-space-950 hover:bg-accent-blue/90 transition"
          >
            Apply Filters
          </button>
        </div>
      </form>

      {/* Candidate Data Table */}
      <div className="overflow-x-auto rounded-xl border border-space-border bg-space-850">
        <table className="w-full text-left border-collapse text-xs font-mono">
          <thead>
            <tr className="border-b border-space-border bg-space-950/60 text-astro-muted uppercase tracking-wider">
              <th
                onClick={() => handleSort("kepid")}
                className="py-3 px-4 cursor-pointer hover:text-white"
              >
                <div className="flex items-center gap-1">
                  <span>KIC ID</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th className="py-3 px-3">TCE #</th>
              <th
                onClick={() => handleSort("tce_period")}
                className="py-3 px-3 cursor-pointer hover:text-white"
              >
                <div className="flex items-center gap-1">
                  <span>Period (d)</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th className="py-3 px-3">Duration (h)</th>
              <th
                onClick={() => handleSort("tce_depth")}
                className="py-3 px-3 cursor-pointer hover:text-white"
              >
                <div className="flex items-center gap-1">
                  <span>Depth (ppm)</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th
                onClick={() => handleSort("tce_prad")}
                className="py-3 px-3 cursor-pointer hover:text-white"
              >
                <div className="flex items-center gap-1">
                  <span>Radius (R⊕)</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th
                onClick={() => handleSort("tce_model_snr")}
                className="py-3 px-3 cursor-pointer hover:text-white"
              >
                <div className="flex items-center gap-1">
                  <span>SNR</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th className="py-3 px-3">Disposition</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-space-border/50 text-astro-text">
            {loading ? (
              <tr>
                <td colSpan={9} className="py-12 text-center text-astro-subtle">
                  Loading NASA DR24 candidates...
                </td>
              </tr>
            ) : candidates.length === 0 ? (
              <tr>
                <td colSpan={9} className="py-12 text-center text-astro-subtle">
                  No candidate signals match the specified filters.
                </td>
              </tr>
            ) : (
              candidates.map((c) => (
                <tr key={`${c.kepid}_${c.tce_plnt_num}`} className="hover:bg-space-800/60 transition">
                  <td className="py-3 px-4 font-bold text-accent-blue">{c.kepid}</td>
                  <td className="py-3 px-3 text-astro-muted">{c.tce_plnt_num}</td>
                  <td className="py-3 px-3">{c.tce_period ? c.tce_period.toFixed(4) : "—"}</td>
                  <td className="py-3 px-3">{c.tce_duration ? c.tce_duration.toFixed(2) : "—"}</td>
                  <td className="py-3 px-3">{c.tce_depth ? c.tce_depth.toFixed(1) : "—"}</td>
                  <td className="py-3 px-3">{c.tce_prad ? c.tce_prad.toFixed(2) : "—"}</td>
                  <td className="py-3 px-3 font-semibold text-accent-cyan">
                    {c.tce_model_snr ? c.tce_model_snr.toFixed(1) : "—"}
                  </td>
                  <td className="py-3 px-3">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                        c.av_training_set === "PC"
                          ? "bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/30"
                          : c.av_training_set === "AFP"
                          ? "bg-accent-rose/10 text-accent-rose border border-accent-rose/30"
                          : "bg-accent-gold/10 text-accent-gold border border-accent-gold/30"
                      }`}
                    >
                      {c.av_training_set || "UNKNOWN"}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Link
                        href={`/detector?kepid=${c.kepid}&tce_plnt_num=${c.tce_plnt_num}`}
                        className="inline-flex items-center gap-1 rounded bg-accent-blue/10 px-2 py-1 text-[11px] font-medium text-accent-blue hover:bg-accent-blue hover:text-space-950 transition"
                      >
                        <Telescope className="h-3 w-3" />
                        Inference
                      </Link>
                      <Link
                        href={`/studio?kepid=${c.kepid}`}
                        className="inline-flex items-center gap-1 rounded bg-space-800 px-2 py-1 text-[11px] text-astro-muted hover:text-white transition"
                      >
                        <Radio className="h-3 w-3" />
                        Curve
                      </Link>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center justify-between text-xs font-mono text-astro-muted">
        <div>
          Showing Page <strong className="text-astro-text">{page}</strong> of{" "}
          <strong className="text-astro-text">{totalPages.toLocaleString()}</strong>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page <= 1}
            className="flex items-center gap-1 rounded-lg border border-space-border bg-space-850 px-3 py-1.5 hover:bg-space-800 disabled:opacity-40 transition"
          >
            <ChevronLeft className="h-4 w-4" />
            Prev
          </button>
          <button
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page >= totalPages}
            className="flex items-center gap-1 rounded-lg border border-space-border bg-space-850 px-3 py-1.5 hover:bg-space-800 disabled:opacity-40 transition"
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

