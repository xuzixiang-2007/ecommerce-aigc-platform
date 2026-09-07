/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f2f7ff",
          100: "#e5eaff",
          200: "#a9aeff",
          500: "#6f6fff",
          600: "#4b3fe3",
          700: "#3c2eca",
          900: "#1a1759",
        },
      },
    },
  },
  plugins: [],
}
