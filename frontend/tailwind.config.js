/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          50: "#eef2f7",
          100: "#d4dee9",
          200: "#a9bdd3",
          300: "#7e9bbd",
          400: "#4d6f97",
          500: "#305178",
          600: "#1f3a5f",
          700: "#152a45",
          800: "#0f1f33",
          900: "#0a1622",
          950: "#060d15",
        },
        gold: {
          50: "#fdf8ec",
          100: "#faf0d2",
          200: "#f3dea3",
          300: "#eac66d",
          400: "#dfa93e",
          500: "#c98a24",
          600: "#a86c1c",
          700: "#86541c",
          800: "#6d451c",
          900: "#5c3a1b",
        },
      },
      backgroundImage: {
        "navy-gradient": "linear-gradient(135deg, #152a45 0%, #0a1622 100%)",
        "gold-gradient": "linear-gradient(135deg, #dfa93e 0%, #a86c1c 100%)",
      },
      boxShadow: {
        card: "0 1px 2px 0 rgb(15 31 51 / 0.04), 0 1px 3px 0 rgb(15 31 51 / 0.08)",
        "card-hover": "0 4px 12px 0 rgb(15 31 51 / 0.10)",
      },
    },
  },
  plugins: [],
};
