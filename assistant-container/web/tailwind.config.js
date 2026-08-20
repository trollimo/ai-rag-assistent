/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: { extend: {} },
  // TODO: npm install @tailwindcss/typography failed here (flaky registry
  // connection) — package.json already lists it, install it and uncomment
  // once network cooperates, for proper `prose` markdown styling.
  // plugins: [require("@tailwindcss/typography")],
  plugins: [],
};
