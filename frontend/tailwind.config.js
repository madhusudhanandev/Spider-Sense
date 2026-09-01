/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        void: "#0A0B0E",
        navy: {
          DEFAULT: "#0F1420",
          surface: "#151C2C",
          border: "#232C40",
        },
        spider: {
          red: "#E8322B",
          "red-dim": "#7A1E1B",
        },
        web: {
          blue: "#3E7BFA",
          "blue-dim": "#1E3A66",
        },
        ink: {
          primary: "#EDEFF3",
          muted: "#8B93A7",
          faint: "#545C70",
        },
        risk: {
          low: "#4ADE80",
          medium: "#FBBF24",
          high: "#F97316",
          critical: "#E8322B",
        },
      },
      fontFamily: {
        display: ["\"Source Serif 4\"", "Georgia", "serif"],
        sans: ["\"IBM Plex Sans\"", "system-ui", "sans-serif"],
        condensed: ["\"Barlow Condensed\"", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "web-radial": "radial-gradient(circle at center, rgba(62,123,250,0.10) 0%, rgba(10,11,14,0) 70%)",
      },
    },
  },
  plugins: [],
};
