import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#7e22ce", 
          dark: "#6b21a8",
          light: "#a855f7",
        },
      },
    },
  },
  plugins: [],
}
export default config
