import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0a0c10",
        surface: "#111418",
        "surface-2": "#1a1f26",
        border: "#2a313a",
        "text-primary": "#f1f5f9",
        "text-secondary": "#94a3b8",
        accent: "#00d4aa",
        "accent-dark": "#00b38f",
        warning: "#f59e0b",
      },
      fontFamily: {
        mono: ["var(--font-geist-mono)", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
