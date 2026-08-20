"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { AnswerSource, Turn, topicLabel } from "./types";

const BADGE: Record<AnswerSource, { icon: string; label: string; className: string }> = {
  rag: {
    icon: "📚",
    label: "Из базы знаний",
    className: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
  },
  llm_knowledge: {
    icon: "🧠",
    label: "Общие знания LLM — не из базы",
    className: "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
  },
  no_info: {
    icon: "❔",
    label: "Нет данных",
    className: "bg-gray-100 text-gray-500 dark:bg-neutral-800 dark:text-neutral-400",
  },
};

export default function AnswerPanel({
  turn,
  onAskRelated,
}: {
  turn: Turn | null;
  onAskRelated: (question: string) => void;
}) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  if (!turn) {
    return (
      <div className="h-full flex items-center justify-center text-gray-300 dark:text-neutral-700">
        <div className="text-center">
          <div className="text-5xl mb-3">💬</div>
          <p className="text-sm">Ответ появится здесь</p>
        </div>
      </div>
    );
  }

  const toggle = (source: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(source)) next.delete(source);
      else next.add(source);
      return next;
    });
  };

  const badge = BADGE[turn.answer_source];

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-3xl mx-auto px-8 py-8">
        {/* Question header */}
        <div className="mb-6">
          <div className="text-xs font-medium text-blue-500 dark:text-blue-400 uppercase tracking-wide mb-1">
            Вопрос
          </div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-neutral-100">{turn.question}</h2>
          {turn.normalized_query && (
            <p className="text-xs text-gray-400 dark:text-neutral-500 mt-1">
              🔍 искали как: «{turn.normalized_query}»
            </p>
          )}
        </div>

        {/* Answer slide */}
        <div className="bg-white dark:bg-neutral-900 rounded-2xl shadow-sm ring-1 ring-gray-200 dark:ring-neutral-700 p-6">
          {turn.loading ? (
            <div className="flex items-center gap-2 text-gray-400 dark:text-neutral-500 text-sm">
              <span className="inline-block w-2 h-2 bg-gray-300 dark:bg-neutral-600 rounded-full animate-bounce" />
              <span className="inline-block w-2 h-2 bg-gray-300 dark:bg-neutral-600 rounded-full animate-bounce [animation-delay:0.15s]" />
              <span className="inline-block w-2 h-2 bg-gray-300 dark:bg-neutral-600 rounded-full animate-bounce [animation-delay:0.3s]" />
              <span className="ml-1">Формирую ответ...</span>
            </div>
          ) : turn.error ? (
            <p className="text-sm text-red-500">{turn.error}</p>
          ) : (
            <>
              {turn.answer_source !== "no_info" && (
                <div
                  className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full mb-4 ${badge.className}`}
                >
                  <span>{badge.icon}</span>
                  <span>{badge.label}</span>
                </div>
              )}
              <div className="answer-markdown prose prose-sm dark:prose-invert max-w-none prose-pre:bg-gray-900 prose-pre:text-gray-100">
                <ReactMarkdown>{turn.answer}</ReactMarkdown>
              </div>
            </>
          )}

          {!turn.loading && !turn.error && turn.sources.length > 0 && (
            <div className="mt-5 pt-4 border-t border-gray-100 dark:border-neutral-800 space-y-1.5">
              <span className="text-xs text-gray-400 dark:text-neutral-500">Источники (нажмите, чтобы раскрыть):</span>
              <div className="flex flex-wrap gap-1.5">
                {turn.sources.map((s) => (
                  <button
                    key={s.source}
                    onClick={() => toggle(s.source)}
                    className={`text-xs px-2 py-0.5 rounded-full transition-colors ${
                      expanded.has(s.source)
                        ? "bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                        : "bg-gray-100 text-gray-600 dark:bg-neutral-800 dark:text-neutral-300 hover:bg-gray-200 dark:hover:bg-neutral-700"
                    }`}
                  >
                    {topicLabel(s.source)}
                  </button>
                ))}
              </div>
              {turn.sources
                .filter((s) => expanded.has(s.source))
                .map((s) => (
                  <div
                    key={s.source}
                    className="mt-2 text-xs bg-gray-50 dark:bg-neutral-800 rounded-lg p-3 space-y-2 text-gray-700 dark:text-neutral-300"
                  >
                    <div className="font-medium text-gray-500 dark:text-neutral-400">{s.source}</div>
                    {s.chunks.map((c) => (
                      <pre key={c.chunk} className="whitespace-pre-wrap font-sans">
                        {c.text}
                      </pre>
                    ))}
                  </div>
                ))}
            </div>
          )}
        </div>

        {/* Related topics */}
        {!turn.loading && turn.related_topics.length > 0 && (
          <div className="mt-6">
            <div className="text-xs font-medium text-gray-400 dark:text-neutral-500 uppercase tracking-wide mb-3">
              Не хотите узнать ещё об этом?
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {turn.related_topics.map((rt) => (
                <button
                  key={rt.source}
                  onClick={() => onAskRelated(`Расскажи про ${topicLabel(rt.source)}`)}
                  className="text-left bg-white dark:bg-neutral-900 rounded-xl ring-1 ring-gray-200 dark:ring-neutral-700 p-4 hover:ring-blue-300 dark:hover:ring-blue-700 hover:shadow-sm transition-all"
                >
                  <div className="font-medium text-sm text-gray-800 dark:text-neutral-200">
                    {topicLabel(rt.source)}
                  </div>
                  {rt.snippet && (
                    <div className="text-xs text-gray-400 dark:text-neutral-500 mt-1 line-clamp-2">
                      {rt.snippet}
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
