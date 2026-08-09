/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./bloggr/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "var(--canvas)",
        surface: "var(--surface)",
        surface2: "var(--surface2)",
        imageframe: "var(--imageframe)",
        ink: "var(--ink)",
        ink2: "var(--ink2)",
        ink3: "var(--ink3)",
        line: "var(--line)",
        accent: "var(--accent)",
        mint: "#3cffd0",
        mintborder: "#309875",
        uv: "#5200ff",
        uvrule: "#3d00bf",
        linkblue: "#3860be",
        focuscyan: "#1eaedb",
        dim: "#8c8c8c",
        "tile-yellow": "#ffe600",
        "tile-pink": "#ff4fa3",
        "tile-orange": "#ff7a1f",
        "tile-blue": "#0f8bff",
        "tile-purple": "#5200ff",
        "tile-mint": "#3cffd0",
        "tile-white": "#ffffff",
      },
      fontFamily: {
        display: ["Anton", "Impact", "Helvetica", "sans-serif"],
        sans: ["\"Space Grotesk\"", "Helvetica", "Arial", "sans-serif"],
        mono: ["\"Space Mono\"", "\"Courier New\"", "Courier", "monospace"],
        serif: ["Newsreader", "Georgia", "serif"],
      },
      borderRadius: {
        verge: "20px",
        feature: "24px",
        promo: "30px",
        cta: "40px",
      },
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
  ],
}
