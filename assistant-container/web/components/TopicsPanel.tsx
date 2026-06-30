"use client";

import { useState } from "react";

type TopicItem = {
  source: string;
  source_name: string;
  chunks: number;
  snippet: string;
};

type TopicsResponse = {
  topics: TopicItem[];
  total: number;
};

const API_URL = process.env.NEXT_PUBLIC_FASTAPI_URL || "http://localhost:8000";

function topicLabel(source: string): string {
  const parts = source.replace(/\\/g, "/").split("/");
  return parts[parts.length - 1] || source;
}

export default function TopicsPanel() {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [topics, setTopics] = useState<TopicItem[]>([]);
  const [filter, setFilter] = useState("");
  const [error, setError] = useState("");

  const fetchTopics = async (f: string) => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/topics`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filter: f, top_k: 20 }),
      });
      const data: TopicsResponse = await res.json();
      setTopics(data.topics || []);
    } catch {
      setError("Ошибка загрузки тем");
    } finally {
      setLoading(false);
    }
  };

  const toggle = () => {
    const next = !open;
    setOpen(next);
    if (next && topics.length === 0) {
      fetchTopics("");
    }
  };

  const onSearch = (val: string) => {
    setFilter(val);
    fetchTopics(val);
  };

  return (
    <div className="mt-4 bg-white rounded-lg shadow">
      <button
        className="w-full flex items-center justify-between px-4 py-3 text-left font-medium text-gray-700 hover:bg-gray-50 rounded-lg"
        onClick={toggle}
      >
        <span>📋 Просмотр тем из RAG</span>
        <span className="text-gray-400">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="px-4 pb-3 border-t border-gray-100">
          <input
            className="w-full border rounded-lg px-3 py-2 mt-3 mb-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="Поиск по темам..."
            value={filter}
            onChange={(e) => onSearch(e.target.value)}
          />

          {loading && <p className="text-sm text-gray-400">Загрузка...</p>}
          {error && <p className="text-sm text-red-500">{error}</p>}

          {!loading && !error && topics.length === 0 && (
            <p className="text-sm text-gray-400">Ничего не найдено</p>
          )}

          {!loading && topics.length > 0 && (
            <ul className="space-y-2 max-h-64 overflow-y-auto">
              {topics.map((t) => (
                <li key={t.source} className="text-sm border-b border-gray-50 pb-2">
                  <div className="font-medium text-gray-800">{topicLabel(t.source)}</div>
                  <div className="text-xs text-gray-400">
                    {t.chunks} чанк{t.chunks > 1 ? "ов" : ""}
                    {t.source_name ? ` · ${t.source_name}` : ""}
                  </div>
                  {t.snippet && (
                    <div className="text-xs text-gray-500 mt-1 truncate">{t.snippet}</div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
