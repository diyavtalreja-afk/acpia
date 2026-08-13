/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: "#FCF9F7",
        card: "#EBE2E0",
        edge: "#D1C8C6",
        accent: "#835E54",
        ok: "#22C55E",
        warn: "#F59E0B",
        danger: "#EF4444",
        ink: "#443728",
        mut: "#835E54",
        brown: "#835E54",
        surface: "#EBE2E0",
        border: "#D1C8C6",
        main: "#FCF9F7",
      },
      fontFamily: {
        sans: ["Open Sans", "InterVariable", "Inter", "system-ui", "sans-serif"],
        serif: ["Georgia", "Cambria", "serif"],
      },
      keyframes: {
        fadein: {
          "0%": { opacity: "0", transform: "translateY(2px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseNode: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.45" },
        },
        blink: {
          "0%, 80%, 100%": { opacity: "0.25" },
          "40%": { opacity: "1" },
        },
      },
      animation: {
        fadein: "fadein .25s ease-out both",
        pulseNode: "pulseNode 1.6s ease-in-out infinite",
        blink: "blink 1.2s infinite",
      },
    },
  },
  plugins: [],
};
