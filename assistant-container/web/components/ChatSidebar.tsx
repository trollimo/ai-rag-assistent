"use client";

import { useEffect, useRef } from "react";
import { Turn } from "./types";

export default function ChatSidebar({
  turns,
  activeId,
  onSelect,
  input,
  setInput,
  onSend,
  disabled,
}: {
  turns: Turn[];
  activeId: number | null;
  onSelect: (id: number) => void;
  input: string;
  setInput: (v: string) => void;
  onSend: () => void;
  disabled: boolean;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns.length]);

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-4 border-b border-gray-200">
        <h1 className="text-lg font-semibold text-gray-800">RAG Ассистент</h1>
        <p className="text-xs text-gray-400 mt-0.5">Стандарты разработки</p>
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
        {turns.length === 0 && (
          <p className="text-sm text-gray-400 px-2 py-4">
            Задайте вопрос по базе знаний — ответ появится справа.
          </p>
        )}
        {turns.map((t) => (
          <button
            key={t.id}
            onClick={() => onSelect(t.id)}
            className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors ${
              t.id === activeId
                ? "bg-blue-50 text-blue-900 ring-1 ring-blue-200"
                : "text-gray-700 hover:bg-gray-100"
            }`}
          >
            <div className="truncate font-medium">{t.question}</div>
            {t.loading ? (
              <div className="text-xs text-gray-400 mt-0.5">Печатает…</div>
            ) : t.error ? (
              <div className="text-xs text-red-400 mt-0.5">Ошибка</div>
            ) : (
              <div className="text-xs text-gray-400 mt-0.5 truncate">{t.answer}</div>
            )}
          </button>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="p-3 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            className="flex-1 border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
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
