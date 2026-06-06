import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Palette tuned to the takeUforward judge screenshot.
        bg: {
          DEFAULT: "#0f1117", // app background
          panel: "#16181f",   // panels
          raised: "#1c1f28",  // cards / inputs
          hover: "#232733",
        },
        edge: "#262a35",       // borders
        accent: {
          DEFAULT: "#8b7cf6",  // purple
          soft: "#a99bff",
        },
        brand: "#f97316",      // orange (Now your turn / Easy chips)
        ok: "#22c55e",
        bad: "#ef4444",
        warn: "#eab308",
        diff: {
          easy: "#22c55e",
          medium: "#eab308",
          hard: "#ef4444",
        },
        ink: {
          DEFAULT: "#e6e8ee",
          dim: "#9aa1b1",
          faint: "#6b7280",
        },
      },
      fontFamily: {
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
