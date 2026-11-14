"use client";

import React, { useMemo } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  AreaChart,
  Area,
} from "recharts";

interface LightCurveChartProps {
  xData: number[];
  yData: number[];
  attribution?: number[];
  xLabel?: string;
  yLabel?: string;
  title?: string;
  color?: string;
  height?: number;
  showAttribution?: boolean;
}

export default function LightCurveChart({
  xData,
  yData,
  attribution,
  xLabel = "Phase",
  yLabel = "Normalized Flux",
  title,
  color = "#63B3FF",
  height = 280,
  showAttribution = false,
}: LightCurveChartProps) {
  const chartData = useMemo(() => {
    if (!xData || !yData || xData.length === 0) return [];
    // Downsample if over 600 points for smooth svg rendering in React
    const maxPts = 500;
    const step = Math.max(1, Math.floor(xData.length / maxPts));

    const result = [];
    for (let i = 0; i < xData.length; i += step) {
      result.push({
        x: Number(xData[i].toFixed(4)),
        flux: Number(yData[i].toFixed(5)),
        attribution: attribution && attribution[i] !== undefined ? Number(attribution[i].toFixed(6)) : 0,
      });
    }
    return result;
  }, [xData, yData, attribution]);

  if (chartData.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center rounded-lg border border-space-border bg-space-900 text-xs text-astro-subtle font-mono">
        No photometric data to display
      </div>
    );
  }

  // Calculate dynamic domain
  const yVals = chartData.map((d) => d.flux);
  const minY = Math.min(...yVals);
  const maxY = Math.max(...yVals);
  const padding = (maxY - minY) * 0.1 || 0.005;

  return (
    <div className="rounded-xl border border-space-border bg-space-850 p-4 space-y-2">
      {title && (
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-mono font-semibold text-astro-text uppercase tracking-wider">
            {title}
          </h4>
          <span className="text-[11px] font-mono text-astro-subtle">
            {xData.length} Bins
          </span>
        </div>
      )}

      <div style={{ width: "100%", height }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E2D4A" />
            <XAxis
              dataKey="x"
              stroke="#627591"
              tick={{ fill: "#627591", fontSize: 10, fontFamily: "monospace" }}
              tickFormatter={(v) => v.toFixed(3)}
            />
            <YAxis
              domain={[minY - padding, maxY + padding]}
              stroke="#627591"
              tick={{ fill: "#627591", fontSize: 10, fontFamily: "monospace" }}
              tickFormatter={(v) => v.toFixed(4)}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0D1424",
                borderColor: "#1E2D4A",
                borderRadius: "8px",
                color: "#F4F7FF",
                fontSize: "11px",
                fontFamily: "monospace",
              }}
              formatter={(value: any, name: any) => [
                Number(value).toFixed(5),
                name === "flux" ? yLabel : "Attribution",
              ]}
              labelFormatter={(label) => `${xLabel}: ${label}`}
            />
            <Line
              type="monotone"
              dataKey="flux"
              stroke={color}
              strokeWidth={1.8}
              dot={false}
              isAnimationActive={false}
            />
            {showAttribution && attribution && (
              <Line
                type="monotone"
                dataKey="attribution"
                stroke="#38D9A9"
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={false}
                isAnimationActive={false}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="flex justify-between text-[11px] font-mono text-astro-subtle">
        <span>{xLabel}</span>
        {showAttribution && (
          <span className="flex items-center gap-1.5 text-accent-cyan">
            <span className="h-1.5 w-1.5 rounded-full bg-accent-cyan" />
            1D Integrated Gradients Attribution
          </span>
        )}
      </div>
    </div>
  );
}

