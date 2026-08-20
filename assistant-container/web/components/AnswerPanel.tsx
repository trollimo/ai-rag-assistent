"use client";

import ReactMarkdown from "react-markdown";
import { Turn, topicLabel } from "./types";

export default function AnswerPanel({
  turn,
  onAskRelated,
}: {
  turn: Turn | null;
  onAskRelated: (question: string) => void;
}) {
  if (!turn) {
    return (
      <div className="h-full flex items-center justify-center text-gray-300">
        <div className="text-center">
          <div className="text-5xl mb-3">💬</div>
          <p className="text-sm">Ответ появится здесь</p>
        </div>
      </div>
    );
  }

  const sourceNames = Array.from(new Set(turn.sources.map((s) => topicLabel(s.source))));

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-3xl mx-auto px-8 py-8">
        {/* Question header */}
        <div className="mb-6">
          <div className="text-xs font-medium text-blue-500 uppercase tracking-wide mb-1">Вопрос</div>
          <h2 className="text-xl font-semibold text-gray-900">{turn.question}</h2>
        </div>

        {/* Answer slide */}
        <div className="bg-white rounded-2xl shadow-sm ring-1 ring-gray-100 p-6">
          {turn.loading ? (
            <div className="flex items-center gap-2 text-gray-400 text-sm">
              <span className="inline-block w-2 h-2 bg-gray-300 rounded-full animate-bounce" />
              <span className="inline-block w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:0.15s]" />
              <span className="inline-block w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:0.3s]" />
              <span className="ml-1">Формирую ответ...</span>
            </div>
          ) : turn.error ? (
            <p className="text-sm text-red-500">{turn.error}</p>
          ) : (
            <div className="answer-markdown prose prose-sm max-w-none prose-pre:bg-gray-900 prose-pre:text-gray-100">
              <ReactMarkdown>{turn.answer}</ReactMarkdown>
            </div>
          )}

          {!turn.loading && !turn.error && sourceNames.length > 0 && (
            <div className="mt-5 pt-4 border-t border-gray-100 flex flex-wrap gap-1.5">
              <span className="text-xs text-gray-400 mr-1">Источники:</span>
              {sourceNames.map((name) => (
                <span
                  key={name}
                  className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full"
                >
                  {name}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Related topics */}
        {!turn.loading && turn.related_topics.length > 0 && (
          <div className="mt-6">
            <div className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-3">
              Не хотите узнать ещё об этом?
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {turn.related_topics.map((rt) => (
                <button
                  key={rt.source}
                  onClick={() => onAskRelated(`Расскажи про ${topicLabel(rt.source)}`)}
                  className="text-left bg-white rounded-xl ring-1 ring-gray-100 p-4 hover:ring-blue-200 hover:shadow-sm transition-all"
                >
                  <div className="font-medium text-sm text-gray-800">{topicLabel(rt.source)}</div>
                  {rt.snippet && (
                    <div className="text-xs text-gray-400 mt-1 line-clamp-2">{rt.snippet}</div>
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
