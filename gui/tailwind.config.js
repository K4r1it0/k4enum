/** @type {import('tailwindcss').Config} */
const colors = require("tailwindcss/colors");
module.exports = {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
    "./error.vue",
  ],
  darkMode: "class",
  theme: {
    colors: {
      primary: "#020420",
      placeholder: "#a1a1aa",
      border: "#27272a",
      "active-border": "#3f3f46",
      "active-bg": "#18181b",
      active: "#818cf8",
      body: "#09090b",
      transparent: "transparent",
      red: colors.red,
      black: colors.black,
      white: colors.white,
      gray: colors.gray,
      emerald: colors.emerald,
      indigo: colors.indigo,
      yellow: colors.yellow,
      green: colors.green,
    },
    extend: {},
    screens: {
      sm: "576px",
      // => @media (min-width: 640px) { ... }
      md: "768px",
      // => @media (min-width: 768px) { ... }
      lg: "992px",
      // => @media (min-width: 992px) { ... }
      xl: "1200px",
      // => @media (min-width: 1280px) { ... }
      "2xl": "1400px",
      // => @media (min-width: 1536px) { ... }
    },
    container: {
      center: true,
      padding: {
        DEFAULT: "1rem",
        // sm: "1.5rem",
        // lg: "2rem",
        // xl: "3rem",
        // "2xl": "4rem",
      },
    },
  },
  plugins: [],
};
