"use client";

import { useEffect, useRef, useState } from "react";

function applyTheme(dark: boolean) {
  document.documentElement.classList.toggle("dark", dark);
  localStorage.setItem("theme", dark ? "dark" : "light");
}

function Switch({ on, onClick }: { on: boolean; onClick: () => void }) {
  return (
    <button
      role="switch"
      aria-checked={on}
      onClick={onClick}
      className={`relative w-9 h-5 rounded-full transition-colors shrink-0 ${
        on ? "bg-blue-600" : "bg-gray-300 dark:bg-neutral-600"
      }`}
    >
      <span
        className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform ${
          on ? "translate-x-4" : ""
        }`}
      />
    </button>
  );
}

export default function SettingsMenu({
  normalizeQuery,
  setNormalizeQuery,
}: {
  normalizeQuery: boolean;
  setNormalizeQuery: (v: boolean) => void;
}) {
  const [dark, setDark] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const stored = localStorage.getItem("theme");
    const initial = stored ? stored === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
    setDark(initial);
    applyTheme(initial);
    setMounted(true);
  }, []);

  useEffect(() => {
    const onClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  if (!mounted) return <div className="w-8 h-8" />;

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 dark:text-neutral-400 hover:text-gray-700 dark:hover:text-neutral-200 hover:bg-gray-100 dark:hover:bg-neutral-800 transition-colors"
        title="Настройки"
      >
        ⚙️
      </button>

      {open && (
        <div className="absolute bottom-full right-0 mb-2 w-64 bg-white dark:bg-neutral-800 rounded-xl shadow-lg ring-1 ring-gray-200 dark:ring-neutral-700 p-3 space-y-3 z-20">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700 dark:text-neutral-200">
              {dark ? "🌙 Тёмная тема" : "☀️ Светлая тема"}
            </div>
            <Switch
              on={dark}
              onClick={() => {
                const next = !dark;
                setDark(next);
                applyTheme(next);
              }}
            />
          </div>

          <div className="border-t border-gray-100 dark:border-neutral-700 pt-3">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-700 dark:text-neutral-200">Нормализация запроса</div>
              <Switch on={normalizeQuery} onClick={() => setNormalizeQuery(!normalizeQuery)} />
            </div>
            <p className="text-xs text-gray-400 dark:text-neutral-500 mt-1">
              Доп. запрос к LLM разворачивает сленг ("кубер" → "Kubernetes") перед
              поиском — точнее, но на 1 обращение к LLM дольше. Выключайте для
              тестирования.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
