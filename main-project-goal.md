Ниже даю **детальное markdown-задание для агентов**. Я также немного нормализовал архитектуру: у тебя получается 2 слоя — `rag-generation` для офлайн-построения базы знаний и `assistant-container` для runtime-приложения с Web UI + MCP. [open-code](https://open-code.ai/docs/en/mcp-servers)

***

# Задание для разработки RAG + MCP системы

## Цель проекта

Нужно разработать локальную, офлайн-ориентированную систему знаний, которая работает по двум сценариям:

- **Человек → Web UI → программа → ответ из RAG**.
- **Агент ИИ → MCP → программа → ответ из RAG**.

Система должна работать внутри Docker-контейнеров и **не делать интернет-запросов во время обработки знаний и ответов**. Интернет допускается только на этапе первоначальной загрузки зависимостей/моделей, если это явно разрешено.

***

Да — для твоего случая **веб-часть лучше делать на Next.js**, а backend для web-части — на **FastAPI**. Такой стек удобен для чата: Next.js даёт современный UI, а FastAPI держит API, RAG retrieval и вызов локальной модели; похожая схема часто используется в full-stack chatbot-проектах. [youtube](https://www.youtube.com/watch?v=aXVuA857ySA)
Я обновил задание ниже так, чтобы это было явно зафиксировано.

***

# Обновлённое ТЗ: локальный AI-RAG ассистент с Web UI и MCP

## Цель проекта

Создать локальную систему знаний с двумя способами доступа:
- **Человек → Web UI (Next.js) → FastAPI backend → RAG → локальная модель → ответ**.
- **Агент ИИ → MCP → FastAPI backend / RAG-сервис → локальная модель → ответ**.

Система должна работать в Docker и не выполнять интернет-запросы во время обработки знаний и runtime-ответов. OpenCode должен получать знания через локальный MCP-сервер. [open-code](https://open-code.ai/ru/docs/mcp-servers)

## Технологический стек

### Web-часть
- **Frontend:** Next.js.
- **Почему:** удобно строить окно чата, поток сообщений, markdown-рендеринг, состояние диалога и загрузку ответов. [medium](https://medium.com/@charlieozil39/building-a-scalable-chatbot-web-app-with-fastapi-groq-llm-and-docker-e379c7a1e2d2)

### Backend для web-части
- **Backend:** FastAPI.
- **Почему:** простой API для чата, интеграции с retrieval, orchestration RAG и локальной моделью. [github](https://github.com/vercel-labs/nextjs-fastapi-chat-app-starter)

### RAG-часть
- **Vector DB:** ChromaDB.
- **Embeddings:** локальная sentence-transformers-модель.
- **MCP:** локальный MCP server для OpenCode. [opencode](https://opencode.ai/docs/mcp-servers/)

***

## Архитектура

### Сценарий человека
`Browser → Next.js chat UI → FastAPI /chat → retrieval in ChromaDB → local LLM → response`

### Сценарий агента
`OpenCode agent → MCP tool search_docs → FastAPI RAG service → local context → response`

### Поток RAG
`Markdown docs → chunking → embeddings → ChromaDB → retrieval → prompt → local generation`. [docs.trychroma](https://docs.trychroma.com/guides/build/chunking)

***

## Структура проекта

```text
project-root/
  rag-generation/
    config/
      rag-sources.yaml
    docs/
      rules/
      poetry/
    output/
      chroma_db/
      manifest.json
    src/
      ingest.py
      chunking.py
      embeddings.py
      storage.py
    rag-generate.ps1
    rag-generate.sh
    requirements.txt

  assistant-container/
    app/
      api/
        main.py
      core/
        settings.py
      mcp/
        server.py
      rag/
        retriever.py
        prompts.py
      llm/
        loader.py
      web/
        next_frontend/
          app/
          components/
          styles/
      backend/
        __init__.py
    Dockerfile
    docker-compose.yml
    requirements.txt
    package.json
    next.config.js
```

***

## Принятые архитектурные решения

| Решение | Вывод |
|---------|-------|
| **Модель для embeddings** | ✅ `sentence-transformers/all-MiniLM-L6-v2` |
| **LLM для чата** | ✅ `phi4-mini` (Microsoft, локальная, CPU-friendly) |
| **Web + Backend** | ✅ Next.js + FastAPI — **один Docker-контейнер** (multi-stage: Node build → Python runtime) |
| **MCP server** | ✅ Отдельный процесс (stdio), запускается вне контейнера для OpenCode |
| **Transport MCP** | ✅ stdio (FastMCP) |
| **ChromaDB** | ✅ PersistentClient, монтируется volume из `rag-generation/output/chroma_db` |

> Эти решения зафиксированы и используются во всех модулях проекта.

***

## Ответственность модулей

### `rag-generation`
- читает Markdown-файлы;
- режет на чанки;
- делает embeddings;
- записывает в локальную ChromaDB;
- формирует manifest со списком источников. [datapipes.chromadb](https://datapipes.chromadb.dev/processors/chunking/)

### `assistant-container`
- отдаёт Web UI через Next.js;
- принимает API-запросы через FastAPI;
- выполняет retrieval;
- вызывает локальную модель;
- предоставляет MCP tool для OpenCode. [open-code](https://open-code.ai/ru/docs/mcp-servers)

***

## Последовательность разработки

1. Подготовить Markdown-источники.
2. Описать папки в `rag-sources.yaml`.
3. Реализовать `rag-generation`.
4. Построить ChromaDB.
5. Сделать FastAPI backend.
6. Подключить Next.js chat UI.
7. Добавить MCP-server.
8. Собрать Docker.
9. Проверить offline runtime.
10. Подключить OpenCode через MCP. [opencode](https://opencode.ai/docs/mcp-servers/)

***

## `rag-sources.yaml`

```yaml
sources:
  - name: rules
    path: ./docs/rules
    include:
      - "**/*.md"

  - name: poetry
    path: ./docs/poetry
    include:
      - "**/*.md"

chunking:
  method: markdown_headers_then_fallback
  chunk_size: 1200
  overlap: 200

storage:
  type: chromadb
  path: ./output/chroma_db
  collection: knowledge_base

embeddings:
  model: sentence-transformers/all-MiniLM-L6-v2
```

***

## `rag-generation/src/ingest.py`

```python
from pathlib import Path
import yaml
import chromadb
from sentence_transformers import SentenceTransformer
from chunking import split_markdown

BASE_DIR = Path(__file__).resolve().parent.parent

def load_config():
    with open(BASE_DIR / "config" / "rag-sources.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def iter_md_files(root):
    yield from Path(root).rglob("*.md")

def main():
    cfg = load_config()
    model = SentenceTransformer(cfg["embeddings"]["model"])
    client = chromadb.PersistentClient(path=str(BASE_DIR / "output" / "chroma_db"))
    collection = client.get_or_create_collection(name=cfg["storage"]["collection"])

    docs, ids, metas, embs = [], [], [], []

    for source in cfg["sources"]:
        source_dir = BASE_DIR / source["path"].lstrip("./")
        for file_path in iter_md_files(source_dir):
            text = file_path.read_text(encoding="utf-8")
            chunks = split_markdown(
                text,
                max_chars=cfg["chunking"]["chunk_size"],
                overlap=cfg["chunking"]["overlap"]
            )
            for idx, chunk in enumerate(chunks):
                doc_id = f"{file_path.as_posix()}::{idx}"
                docs.append(chunk)
                ids.append(doc_id)
                metas.append({
                    "source": file_path.as_posix(),
                    "source_name": source["name"],
                    "chunk": idx
                })
                embs.append(model.encode(chunk).tolist())

    if docs:
        collection.add(ids=ids, documents=docs, metadatas=metas, embeddings=embs)

    print(f"Indexed {len(docs)} chunks")

if __name__ == "__main__":
    main()
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

## `assistant-container/app/api/main.py`

```python
from fastapi import FastAPI
from pydantic import BaseModel
from app.rag.retriever import Retriever

app = FastAPI()
retriever = Retriever()

class ChatRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    matches = retriever.search(req.question, top_k=5)
    return {
        "question": req.question,
        "matches": matches,
        "answer": "TODO: подключить локальную мини-модель и генерацию ответа"
    }
```

***

## `assistant-container/app/mcp/server.py`

```python
from mcp.server.fastmcp import FastMCP
from app.rag.retriever import Retriever

mcp = FastMCP("knowledge-rag")
retriever = Retriever()

@mcp.tool()
def search_docs(query: str, top_k: int = 5):
    return {"matches": retriever.search(query, top_k=top_k)}

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

***

## Next.js frontend

### Идея
При открытии web должен открываться **чат в стиле assistant UI**: список сообщений, поле ввода, кнопка отправки, статус “thinking…”, рендер markdown-ответов.

### Минимальный путь
- `app/page.tsx` — окно чата.
- `components/Chat.tsx` — логика сообщений.
- `fetch("/api/chat")` или запрос к FastAPI endpoint.
- TailwindCSS для UI. [github](https://github.com/jondoescoding/fastapi-chatbot-template)

***

## Docker и compose

### `assistant-container/Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `assistant-container/docker-compose.yml`
```yaml
services:
  assistant:
    build: .
    container_name: assistant-container
    ports:
      - "8000:8000"
    volumes:
      - ../rag-generation/output/chroma_db:/data/chroma_db:ro
    environment:
      - RAG_DB_PATH=/data/chroma_db
    restart: unless-stopped
```

***

## Примеры Markdown для обучения

### `docs/rules/coding-rules.md`
```md
# Правила кодирования

## Именование
Классы пишутся в PascalCase. Методы и переменные — в camelCase.

## Структура проекта
Каждый сервис должен иметь отдельную папку. Тесты лежат в папке tests.

## Тестирование
Для каждого публичного метода должен быть unit-тест.
Если меняется логика, нужно обновить тесты и README.

## Проверка перед merge
- код проходит линтер;
- тесты зелёные;
- нет неиспользуемых импортов;
- документированы публичные методы.

## Исключения
Любое отступление от правил должно быть согласовано с техлидом.
```

### `docs/poetry/chorovod-rules.md`
```md
# Правила хоровода

## Основной круг
Хоровод начинается с построения круга по часовой стрелке.

## Отличительные черты
Участники держатся за руки, шаг мягкий, ритм ровный.

## Ведущий
Ведущий задаёт темп и следит, чтобы круг не разрывался.

## Повороты
На поворотах движение замедляется, чтобы все успели синхронизироваться.

## Завершение
Финал хоровода должен быть плавным, без резкой остановки.
```

***

## Тестовые промпты

### Кодирование
```text
Сформируй краткий чеклист правил кодирования и тестирования для команды.
```

### Хоровод
```text
Объясни, как правильно водить хоровод, и перечисли его отличительные черты.
```

### Смешанный
```text
Сравни правила кодирования и правила хоровода. Выдели общую структуру, последовательность и исключения.
```

***

## Итоговая рекомендация

Да, я бы **делал Web UI на Next.js, backend для веба на FastAPI**, а RAG и MCP — как локальные сервисы внутри того же решения. [youtube](https://www.youtube.com/watch?v=aXVuA857ySA)
Так у тебя будет современный чат-интерфейс, нормальный API-слой и отдельный MCP-канал для OpenCode. [open-code](https://open-code.ai/ru/docs/mcp-servers)
