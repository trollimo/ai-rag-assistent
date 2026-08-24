"use client";

import { useEffect, useState } from "react";
import { ShowcaseTopic, getClientId } from "./types";

const API_URL = process.env.NEXT_PUBLIC_FASTAPI_URL || "http://localhost:8000";

export default function RequestsPanel() {
  const [topics, setTopics] = useState<ShowcaseTopic[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const clientId = getClientId();
    fetch(`${API_URL}/requests?client_id=${encodeURIComponent(clientId)}`)
      .then((r) => r.json())
      .then((d) => setTopics(d.topics || []))
      .catch(() => setError("Не удалось загрузить список запросов"));
  }, []);

  const vote = async (topic: ShowcaseTopic) => {
    if (topic.voted) return;
    // Optimistic: the board is a prioritisation aid, a lost vote is not worth
    // making everyone wait on a round-trip for.
    setTopics((prev) =>
      (prev || []).map((t) =>
        t.id === topic.id ? { ...t, voted: true, vote_count: t.vote_count + 1 } : t
      )
    );
    try {
      const res = await fetch(`${API_URL}/requests/${topic.id}/vote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ client_id: getClientId() }),
      });
      const data = await res.json();
      if (typeof data.vote_count === "number") {
        setTopics((prev) =>
          (prev || []).map((t) => (t.id === topic.id ? { ...t, vote_count: data.vote_count } : t))
        );
      }
    } catch {
      setTopics((prev) =>
        (prev || []).map((t) =>
          t.id === topic.id ? { ...t, voted: false, vote_count: Math.max(0, t.vote_count - 1) } : t
        )
      );
    }
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-3xl mx-auto px-8 py-8">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-neutral-100">Запросы</h2>
          <p className="text-sm text-gray-400 dark:text-neutral-500 mt-1">
            Темы, которых не хватает в базе знаний. Голосуйте — что наберёт больше
            голосов, то и добавим раньше.
          </p>
        </div>

        {error && <p className="text-sm text-red-500">{error}</p>}
        {!error && topics === null && (
          <p className="text-sm text-gray-400 dark:text-neutral-500">Загрузка...</p>
        )}
        {topics !== null && topics.length === 0 && (
          <p className="text-sm text-gray-400 dark:text-neutral-500">
            Пока пусто. Темы появляются здесь автоматически, когда несколько человек
            спрашивают об одном и том же, а в базе ответа нет.
          </p>
        )}

        <div className="space-y-2">
          {topics?.map((t) => (
            <div
              key={t.id}
              className="bg-white dark:bg-neutral-900 rounded-xl ring-1 ring-gray-200 dark:ring-neutral-700 p-4 flex items-start gap-4"
            >
              <button
                onClick={() => vote(t)}
                disabled={t.voted}
                title={t.voted ? "Вы уже голосовали" : "Поднять приоритет"}
                className={`shrink-0 w-14 flex flex-col items-center py-1.5 rounded-lg transition-colors ${
                  t.voted
                    ? "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300 cursor-default"
                    : "bg-gray-100 text-gray-600 hover:bg-amber-50 hover:text-amber-700 dark:bg-neutral-800 dark:text-neutral-300 dark:hover:bg-amber-950"
                }`}
              >
                <span className="text-base leading-none">{t.voted ? "★" : "☆"}</span>
                <span className="text-xs font-medium mt-0.5">{t.vote_count}</span>
              </button>

              <div className="min-w-0 flex-1">
                <div className="text-sm font-medium text-gray-900 dark:text-neutral-100">
                  {t.title}
                </div>
                <div className="text-xs text-gray-400 dark:text-neutral-500 mt-1 flex flex-wrap items-center gap-2">
                  <span>спрашивали {t.question_count} раз</span>
                  {t.status === "resolved" && (
                    <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                      ✓ добавлено в базу
                    </span>
                  )}
                </div>
                {t.resolution && (
                  <div className="text-xs text-gray-500 dark:text-neutral-400 mt-1">{t.resolution}</div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
