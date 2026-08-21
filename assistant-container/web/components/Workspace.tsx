"use client";

import { useEffect, useRef, useState } from "react";
import ChatSidebar from "./ChatSidebar";
import AnswerPanel from "./AnswerPanel";
import SkillsPanel from "./SkillsPanel";
import TopicsPanel from "./TopicsPanel";
import SettingsMenu from "./SettingsMenu";
import Mascot, { MascotState } from "./Mascot";
import { ChatMode, Turn } from "./types";

const API_URL = process.env.NEXT_PUBLIC_FASTAPI_URL || "http://localhost:8000";

let nextId = 1;

export default function Workspace() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<ChatMode>("strict");
  const [normalizeQuery, setNormalizeQuery] = useState(true);
  const [rightTab, setRightTab] = useState<"qa" | "skills">("qa");
  const [focusSkill, setFocusSkill] = useState<string | null>(null);

  const openSkill = (name: string) => {
    setFocusSkill(name);
    setRightTab("skills");
  };

  // 384px = 320px (old fixed w-80) * 1.2 -- default 20% wider, then user-resizable.
  const [sidebarWidth, setSidebarWidth] = useState(384);
  const dragging = useRef(false);

  useEffect(() => {
    const stored = localStorage.getItem("sidebarWidth");
    if (stored) setSidebarWidth(Number(stored));
  }, []);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!dragging.current) return;
      setSidebarWidth(Math.min(640, Math.max(260, e.clientX)));
    };
    const onUp = () => {
      if (!dragging.current) return;
      dragging.current = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
      setSidebarWidth((w) => {
        localStorage.setItem("sidebarWidth", String(w));
        return w;
      });
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, []);

  const startResize = () => {
    dragging.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  };

  const anyLoading = turns.some((t) => t.loading);

  const [mascotState, setMascotState] = useState<MascotState>("idle");
  const wasLoading = useRef(false);
  useEffect(() => {
    if (anyLoading) {
      wasLoading.current = true;
      setMascotState("thinking");
      return;
    }
    if (wasLoading.current) {
      wasLoading.current = false;
      setMascotState("happy");
      const t = setTimeout(() => setMascotState("idle"), 2500);
      return () => clearTimeout(t);
    }
  }, [anyLoading]);

  const ask = async (question: string) => {
    if (!question.trim() || anyLoading) return;
    const id = nextId++;
    setInput("");
    setTurns((prev) => [
      ...prev,
      {
        id,
        question,
        answer: "",
        sources: [],
        related_topics: [],
        answer_source: "no_info",
        normalized_query: null,
        skills: [],
        loading: true,
      },
    ]);
    setActiveId(id);
    setRightTab("qa");

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, mode, normalize_query: normalizeQuery }),
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
                answer_source: data.answer_source || "no_info",
                normalized_query: data.normalized_query || null,
                skills: data.skills || [],
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
    <div className="flex h-screen bg-gray-100 dark:bg-neutral-950">
      <aside
        style={{ width: sidebarWidth }}
        className="relative shrink-0 bg-white dark:bg-neutral-900 border-r border-gray-300 dark:border-neutral-700 flex flex-col h-full"
      >
        <div className="flex-1 min-h-0">
          <ChatSidebar
            turns={turns}
            activeId={activeId}
            onSelect={setActiveId}
            input={input}
            setInput={setInput}
            onSend={() => ask(input)}
            disabled={anyLoading}
            mode={mode}
            setMode={setMode}
          />
        </div>
        <div className="shrink-0 max-h-64 overflow-y-auto border-t border-gray-300 dark:border-neutral-700">
          <TopicsPanel />
        </div>
        <div className="shrink-0 border-t border-gray-300 dark:border-neutral-700 px-3 py-2 flex justify-end">
          <SettingsMenu normalizeQuery={normalizeQuery} setNormalizeQuery={setNormalizeQuery} />
        </div>
        {/* Drag handle: invisible until hover, widens the hit area beyond the 1px border */}
        <div
          onMouseDown={startResize}
          className="absolute top-0 right-0 -mr-1 w-2 h-full cursor-col-resize group z-10"
        >
          <div className="w-0.5 h-full mx-auto group-hover:bg-blue-400 dark:group-hover:bg-blue-500 transition-colors" />
        </div>
      </aside>
      <main className="flex-1 min-w-0 flex flex-col h-full">
        <div className="shrink-0 flex gap-1 px-8 pt-4 border-b border-gray-200 dark:border-neutral-800">
          <button
            onClick={() => setRightTab("qa")}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              rightTab === "qa"
                ? "bg-white dark:bg-neutral-900 text-gray-900 dark:text-neutral-100 ring-1 ring-b-0 ring-gray-200 dark:ring-neutral-700"
                : "text-gray-500 dark:text-neutral-400 hover:text-gray-700 dark:hover:text-neutral-200"
            }`}
          >
            Вопрос-ответ
          </button>
          <button
            onClick={() => setRightTab("skills")}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              rightTab === "skills"
                ? "bg-white dark:bg-neutral-900 text-gray-900 dark:text-neutral-100 ring-1 ring-b-0 ring-gray-200 dark:ring-neutral-700"
                : "text-gray-500 dark:text-neutral-400 hover:text-gray-700 dark:hover:text-neutral-200"
            }`}
          >
            Skills
          </button>
        </div>
        <div className="flex-1 min-h-0">
          {rightTab === "qa" ? (
            <AnswerPanel turn={activeTurn} onAskRelated={ask} onOpenSkill={openSkill} />
          ) : (
            <SkillsPanel focusName={focusSkill} />
          )}
        </div>
      </main>
      <Mascot state={mascotState} />
    </div>
  );
}
