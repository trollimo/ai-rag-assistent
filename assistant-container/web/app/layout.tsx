import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "RAG Assistant",
  description: "AI-powered RAG chat",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body className="bg-gray-50 min-h-screen">{children}</body>
    </html>
  );
}
