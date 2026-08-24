"use client";

import { useEffect, useMemo, useState } from "react";
import { CopyButton } from "./AnswerPanel";
import { SkillDetail, SkillSummary } from "./types";

const API_URL = process.env.NEXT_PUBLIC_FASTAPI_URL || "http://localhost:8000";

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} КБ`;
  return `${(bytes / 1024 / 1024).toFixed(1)} МБ`;
}

export default function SkillsPanel({ focusName }: { focusName: string | null }) {
  const [skills, setSkills] = useState<SkillSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [details, setDetails] = useState<Record<string, SkillDetail>>({});
  const [query, setQuery] = useState("");

  // Substring match, name/title hits ranked before description-only hits.
  // Array.sort is stable (spec'd since ES2019), so within each rank the
  // original (backend) order is preserved rather than shuffled.
  const filteredSkills = useMemo(() => {
    if (!skills) return skills;
    const q = query.trim().toLowerCase();
    if (!q) return skills;
    return skills
      .map((s) => {
        const nameHit = s.title.toLowerCase().includes(q) || s.name.toLowerCase().includes(q);
        const descHit = (s.description || "").toLowerCase().includes(q);
        const rank = nameHit ? 0 : descHit ? 1 : -1;
        return { s, rank };
      })
      .filter((x) => x.rank !== -1)
      .sort((a, b) => a.rank - b.rank)
      .map((x) => x.s);
  }, [skills, query]);

  useEffect(() => {
    fetch(`${API_URL}/skills`)
      .then((r) => r.json())
      .then((d) => setSkills(d.skills || []))
      .catch(() => setError("Не удалось загрузить список скиллов"));
  }, []);

  useEffect(() => {
    if (focusName) setExpanded(focusName);
  }, [focusName]);

  const toggle = (name: string) => {
    const next = expanded === name ? null : name;
    setExpanded(next);
    if (next && !details[name]) {
      fetch(`${API_URL}/skills/${name}`)
        .then((r) => r.json())
        .then((d) => setDetails((prev) => ({ ...prev, [name]: d })))
        .catch(() => {});
    }
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-3xl mx-auto px-8 py-8">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-neutral-100">Скиллы</h2>
          <p className="text-sm text-gray-400 dark:text-neutral-500 mt-1">
            Готовые к установке наборы инструкций — скачайте архив и разверните в вашем code-агенте.
          </p>
        </div>

        {skills !== null && skills.length > 0 && (
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Поиск по названию или описанию..."
            className="w-full mb-4 border border-gray-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 text-gray-900 dark:text-neutral-100 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        )}

        {error && <p className="text-sm text-red-500">{error}</p>}
        {!error && skills === null && <p className="text-sm text-gray-400 dark:text-neutral-500">Загрузка...</p>}
        {skills !== null && skills.length === 0 && (
          <p className="text-sm text-gray-400 dark:text-neutral-500">Скиллов в базе пока нет.</p>
        )}
        {skills !== null && skills.length > 0 && filteredSkills?.length === 0 && (
          <p className="text-sm text-gray-400 dark:text-neutral-500">Ничего не найдено по «{query}».</p>
        )}

        <div className="space-y-3">
          {filteredSkills?.map((s) => {
            const isOpen = expanded === s.name;
            const detail = details[s.name];
            return (
              <div
                key={s.name}
                className="bg-white dark:bg-neutral-900 rounded-2xl shadow-sm ring-1 ring-gray-200 dark:ring-neutral-700 overflow-hidden"
              >
                <button onClick={() => toggle(s.name)} className="w-full text-left p-5 flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <div className="font-medium text-gray-900 dark:text-neutral-100">📦 {s.title}</div>
                    {s.description && (
                      <p className="text-sm text-gray-500 dark:text-neutral-400 mt-1 line-clamp-2">{s.description}</p>
                    )}
                    <div className="text-xs text-gray-400 dark:text-neutral-500 mt-2">
                      v{s.version || "—"} · {s.files_count} файлов · {formatSize(s.size_bytes)}
                    </div>
                  </div>
                  <a
                    href={s.download_url}
                    onClick={(e) => e.stopPropagation()}
                    className="shrink-0 flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full bg-blue-600 text-white hover:bg-blue-700"
                  >
                    ⬇ Скачать
                  </a>
                </button>

                {isOpen && (
                  <div className="border-t border-gray-100 dark:border-neutral-800 p-5 pt-4">
                    {!detail ? (
                      <p className="text-sm text-gray-400 dark:text-neutral-500">Загрузка...</p>
                    ) : (
                      <>
                        <div className="text-xs font-medium text-gray-400 dark:text-neutral-500 uppercase tracking-wide mb-2">
                          Файлы в архиве ({detail.files.length})
                        </div>
                        <div className="text-xs font-mono text-gray-600 dark:text-neutral-300 bg-gray-50 dark:bg-neutral-800 rounded-lg p-3 max-h-40 overflow-y-auto space-y-0.5">
                          {detail.files.map((f) => (
                            <div key={f}>{f}</div>
                          ))}
                        </div>

                        <div className="flex items-center justify-between mt-4 mb-2">
                          <span className="text-xs font-medium text-gray-400 dark:text-neutral-500 uppercase tracking-wide">
                            Установка
                          </span>
                          <CopyButton text={detail.install_hint} title="Скопировать команды установки" />
                        </div>
                        <pre className="text-xs bg-gray-900 text-gray-100 rounded-lg p-3 overflow-x-auto whitespace-pre-wrap">
                          {detail.install_hint}
                        </pre>
                      </>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
