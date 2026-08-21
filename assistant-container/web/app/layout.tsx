import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "Архивариус",
  description: "AI-powered RAG chat",
};

const THEME_INIT = `
  try {
    var t = localStorage.getItem('theme');
    var dark = t ? t === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (dark) document.documentElement.classList.add('dark');
  } catch (e) {}
`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <head>
        {/* Runs before hydration so the page doesn't flash the wrong theme */}
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT }} />
      </head>
      <body className="bg-gray-100 dark:bg-neutral-950 min-h-screen">{children}</body>
    </html>
  );
}
