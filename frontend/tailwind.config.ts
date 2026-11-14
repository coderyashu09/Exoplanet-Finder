import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        space: {
          950: "#04070D",
          900: "#070B14",
          850: "#0D1424",
          800: "#111C30",
          700: "#1A2942",
          600: "#223554",
          500: "#314972",
          border: "#1E2D4A",
          borderLight: "#2C4066",
        },
        accent: {
          blue: "#63B3FF",
          purple: "#8B7CFF",
          cyan: "#38D9A9",
          emerald: "#35D49A",
          gold: "#FFBE55",
          rose: "#FF657A",
        },
        astro: {
          text: "#F4F7FF",
          muted: "#9AAAC1",
          subtle: "#627591",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
} satisfies Config;
