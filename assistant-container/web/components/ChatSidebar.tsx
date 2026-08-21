"use client";

import { useEffect, useRef, useState } from "react";
import { ChatMode, Turn } from "./types";

export default function ChatSidebar({
  turns,
  activeId,
  onSelect,
  input,
  setInput,
  onSend,
  disabled,
  mode,
  setMode,
}: {
  turns: Turn[];
  activeId: number | null;
  onSelect: (id: number) => void;
  input: string;
  setInput: (v: string) => void;
  onSend: () => void;
  disabled: boolean;
  mode: ChatMode;
  setMode: (m: ChatMode) => void;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [showHint, setShowHint] = useState(false);
  const [showAboutHint, setShowAboutHint] = useState(false);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns.length]);

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-4 border-b border-gray-200 dark:border-neutral-700">
        <div className="flex items-center gap-1.5">
          <h1 className="text-lg font-semibold text-gray-800 dark:text-neutral-100">Архивариус</h1>
          <div className="relative">
            <button
              aria-label="Как это работает"
              onClick={() => setShowAboutHint((v) => !v)}
              onBlur={() => setShowAboutHint(false)}
              className="w-4 h-4 flex items-center justify-center rounded-full text-[10px] leading-none text-gray-400 dark:text-neutral-500 border border-gray-300 dark:border-neutral-600 hover:text-blue-600 hover:border-blue-400 dark:hover:text-blue-400 dark:hover:border-blue-500"
            >
              ?
            </button>
            {showAboutHint && (
              <div className="absolute top-full left-0 mt-1 w-64 text-xs bg-gray-800 dark:bg-neutral-700 text-white rounded-lg px-3 py-2 shadow-lg z-20">
                Архивариус ищет ответ в базе корпоративных стандартов и инструкций.
                Режим «Только база знаний» отвечает исключительно тем, что там
                нашлось; «База + знания LLM» может дополнить ответ общими
                знаниями модели, если в базе не хватает — такие места отмечаются
                значком 🧠.
              </div>
            )}
          </div>
        </div>
        <p className="text-xs text-gray-400 dark:text-neutral-500 mt-0.5">Стандарты и инструкции</p>
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
        {turns.length === 0 && (
          <p className="text-sm text-gray-400 dark:text-neutral-500 px-2 py-4">
            Задайте вопрос по базе знаний — ответ появится справа.
          </p>
        )}
        {turns.map((t) => (
          <button
            key={t.id}
            onClick={() => onSelect(t.id)}
            className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors ${
              t.id === activeId
                ? "bg-blue-50 dark:bg-blue-950 text-blue-900 dark:text-blue-200 ring-1 ring-blue-200 dark:ring-blue-800"
                : "text-gray-700 dark:text-neutral-300 hover:bg-gray-100 dark:hover:bg-neutral-800"
            }`}
          >
            <div className="truncate font-medium">{t.question}</div>
            {t.loading ? (
              <div className="text-xs text-gray-400 dark:text-neutral-500 mt-0.5">Печатает…</div>
            ) : t.error ? (
              <div className="text-xs text-red-400 mt-0.5">Ошибка</div>
            ) : (
              <div className="text-xs text-gray-400 dark:text-neutral-500 mt-0.5 truncate">{t.answer}</div>
            )}
          </button>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="px-3 pt-2 relative">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-500 dark:text-neutral-400">
            {mode === "strict" ? "Только база знаний" : "База + знания LLM"}
          </span>
          <button
            role="switch"
            aria-checked={mode === "combined"}
            onMouseEnter={() => setShowHint(true)}
            onMouseLeave={() => setShowHint(false)}
            onClick={() => setMode(mode === "strict" ? "combined" : "strict")}
            className={`relative w-9 h-5 rounded-full transition-colors shrink-0 ${
              mode === "combined" ? "bg-blue-600" : "bg-gray-300 dark:bg-neutral-600"
            }`}
          >
            <span
              className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform ${
                mode === "combined" ? "translate-x-4" : ""
              }`}
            />
          </button>
        </div>
        {showHint && (
          <div className="absolute bottom-full right-3 mb-1 w-56 text-xs bg-gray-800 dark:bg-neutral-700 text-white rounded-lg px-3 py-2 shadow-lg z-10">
            Выкл — ответ только из базы знаний, честное «не знаю» если там пусто.
            Вкл — если базы недостаточно, LLM дополнит своими знаниями (с пометкой).
          </div>
        )}
      </div>

      <div className="p-3 border-t border-gray-200 dark:border-neutral-700">
        <div className="flex gap-2">
          <input
            className="flex-1 border border-gray-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 text-gray-900 dark:text-neutral-100 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="Введите вопрос..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !disabled && onSend()}
            disabled={disabled}
          />
          <button
            className="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm hover:bg-blue-700 disabled:opacity-50 shrink-0"
            onClick={onSend}
            disabled={disabled || !input.trim()}
          >
            →
          </button>
        </div>
      </div>
    </div>
  );
}
