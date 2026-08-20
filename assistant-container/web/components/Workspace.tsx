"use client";

import { useState } from "react";
import ChatSidebar from "./ChatSidebar";
import AnswerPanel from "./AnswerPanel";
import TopicsPanel from "./TopicsPanel";
import { Turn } from "./types";

const API_URL = process.env.NEXT_PUBLIC_FASTAPI_URL || "http://localhost:8000";

let nextId = 1;

export default function Workspace() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [input, setInput] = useState("");

  const anyLoading = turns.some((t) => t.loading);

  const ask = async (question: string) => {
    if (!question.trim() || anyLoading) return;
    const id = nextId++;
    setInput("");
    setTurns((prev) => [
      ...prev,
      { id, question, answer: "", sources: [], related_topics: [], loading: true },
    ]);
    setActiveId(id);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setTurns((prev) =>
        prev.map((t) =>
          t.id === id
            ? {
                ...t,
                answer: data.answer || "Нет ответа",
                sources: data.sources || [],
                related_topics: data.related_topics || [],
                loading: false,
              }
            : t
        )
      );
    } catch (e) {
      setTurns((prev) =>
        prev.map((t) =>
          t.id === id ? { ...t, loading: false, error: "Ошибка соединения с сервером" } : t
        )
      );
    }
  };

  const activeTurn = turns.find((t) => t.id === activeId) || null;

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-80 shrink-0 bg-white border-r border-gray-200 flex flex-col h-full">
        <div className="flex-1 min-h-0">
          <ChatSidebar
            turns={turns}
            activeId={activeId}
            onSelect={setActiveId}
            input={input}
            setInput={setInput}
            onSend={() => ask(input)}
            disabled={anyLoading}
          />
        </div>
        <div className="shrink-0 max-h-64 overflow-y-auto border-t border-gray-200">
          <TopicsPanel />
        </div>
      </aside>
      <main className="flex-1 min-w-0">
        <AnswerPanel turn={activeTurn} onAskRelated={ask} />
      </main>
    </div>
  );
}
