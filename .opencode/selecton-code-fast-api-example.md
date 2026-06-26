Да — ниже даю **skeleton code** для Next.js чата и связку с FastAPI. Я взял архитектуру “Next.js frontend + FastAPI backend”, которая хорошо подходит для чат-приложений и часто используется в подобных шаблонах. [github](https://github.com/mazzasaverio/nextjs-fastapi-your-chat)

## Структура фронтенда

```text
assistant-container/
  web/
    app/
      page.tsx
      layout.tsx
      globals.css
    components/
      Chat.tsx
      MessageList.tsx
      MessageInput.tsx
    lib/
      api.ts
    next.config.js
    package.json
    tsconfig.json
```

## `web/app/page.tsx`

```tsx
import Chat from "@/components/Chat";

export default function Page() {
  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100">
      <Chat />
    </main>
  );
}
```

## `web/components/Chat.tsx`

```tsx
"use client";

import { useMemo, useState } from "react";
import { sendChatMessage } from "@/lib/api";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Привет. Задай вопрос по базе знаний.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const canSend = useMemo(() => input.trim().length > 0 && !loading, [input, loading]);

  const onSend = async () => {
    if (!canSend) return;

    const userMessage: Message = { role: "user", content: input.trim() };
    const nextMessages = [...messages, userMessage];

    setMessages(nextMessages);
    setInput("");
    setLoading(true);

    try {
      const data = await sendChatMessage(userMessage.content);
      setMessages([
        ...nextMessages,
        {
          role: "assistant",
          content: data.answer ?? "Ответ не получен.",
        },
      ]);
    } catch {
      setMessages([
        ...nextMessages,
        {
          role: "assistant",
          content: "Ошибка соединения с backend.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-4xl flex-col p-4">
      <div className="mb-4 border-b border-zinc-800 pb-3">
        <h1 className="text-2xl font-semibold">RAG Assistant</h1>
        <p className="text-sm text-zinc-400">Next.js + FastAPI + локальный RAG</p>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto rounded-xl border border-zinc-800 bg-zinc-900 p-4">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={
              m.role === "user"
                ? "ml-auto max-w-[80%] rounded-2xl bg-blue-600 px-4 py-3 text-white"
                : "mr-auto max-w-[80%] rounded-2xl bg-zinc-800 px-4 py-3 text-zinc-100"
            }
          >
            <div className="mb-1 text-xs uppercase tracking-wide opacity-70">
              {m.role}
            </div>
            <div className="whitespace-pre-wrap text-sm leading-6">{m.content}</div>
          </div>
        ))}

        {loading && (
          <div className="mr-auto max-w-[80%] rounded-2xl bg-zinc-800 px-4 py-3 text-zinc-100">
            <div className="text-sm opacity-80">Думаю...</div>
          </div>
        )}
      </div>

      <div className="mt-4 flex gap-2 rounded-xl border border-zinc-800 bg-zinc-900 p-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") onSend();
          }}
          placeholder="Напиши вопрос..."
          className="flex-1 rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm outline-none"
        />
        <button
          onClick={onSend}
          disabled={!canSend}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50"
        >
          Отправить
        </button>
      </div>
    </div>
  );
}
```

## `web/lib/api.ts`

```ts
const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_URL || "http://localhost:8000";

export async function sendChatMessage(question: string) {
  const res = await fetch(`${FASTAPI_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    throw new Error("Failed to send message");
  }

  return res.json();
}
```

## `web/app/layout.tsx`

```tsx
import "./globals.css";

export const metadata = {
  title: "RAG Assistant",
  description: "Local RAG assistant with Next.js and FastAPI",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
```

## `web/app/globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

html, body {
  margin: 0;
  padding: 0;
  background: #09090b;
  color: #fafafa;
  font-family: Arial, Helvetica, sans-serif;
}
```

***

## FastAPI backend

### `assistant-container/app/api/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.rag.retriever import Retriever

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

retriever = Retriever()

class ChatRequest(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    matches = retriever.search(req.question, top_k=5)

    context = "\n\n".join(
        f"[{i+1}] {m['text']}" for i, m in enumerate(matches)
    )

    answer = f"""Ответ на основе RAG-контекста:

{context[:3000]}
"""

    return {
        "question": req.question,
        "matches": matches,
        "answer": answer,
    }
```

***

## `assistant-container/app/rag/retriever.py`

```python
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = Path("/data/chroma_db")
COLLECTION_NAME = "knowledge_base"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

class Retriever:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.client = chromadb.PersistentClient(path=str(DB_PATH))
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

    def search(self, query: str, top_k: int = 5):
        q_emb = self.model.encode(query).tolist()
        result = self.collection.query(query_embeddings=[q_emb], n_results=top_k)

        matches = []
        for doc, meta, dist in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0]
        ):
            matches.append({
                "text": doc,
                "source": meta["source"],
                "chunk": meta["chunk"],
                "distance": dist
            })
        return matches
```

***

## `assistant-container/docker-compose.yml`

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: rag-backend
    ports:
      - "8000:8000"
    volumes:
      - ../rag-generation/output/chroma_db:/data/chroma_db:ro
    environment:
      - RAG_DB_PATH=/data/chroma_db
    restart: unless-stopped

  web:
    image: node:20-alpine
    container_name: rag-web
    working_dir: /app
    command: sh -c "npm install && npm run dev"
    ports:
      - "3000:3000"
    volumes:
      - ./web:/app
    environment:
      - NEXT_PUBLIC_FASTAPI_URL=http://localhost:8000
    depends_on:
      - backend
```

***

## `assistant-container/web/package.json`

```json
{
  "name": "rag-web",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3000"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/react": "^19.0.0",
    "@types/node": "^22.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.5.0",
    "autoprefixer": "^10.4.0"
  }
}
```

***

## Как это будет работать

1. Открываешь `http://localhost:3000`.
2. Видишь окно чата.
3. Пишешь вопрос.
4. Next.js отправляет `POST /chat` на FastAPI.
5. FastAPI делает retrieval по локальной базе.
6. Возвращает ответ.
7. Web показывает ответ в чате. [youtube](https://www.youtube.com/watch?v=aXVuA857ySA)

***

## Что я бы добавил следующим шагом

- markdown-рендер ответов;
- потоковую выдачу token-by-token;
- историю чатов;
- выбор источников;
- MCP endpoint отдельным сервисом;
- нормальный local LLM вместо заглушки ответа.


Для генерации векторной баз embeddings: sentence-transformers/all-MiniLM-L6-v2
Для чата и подготовки ответа LLM: phi4-mini 