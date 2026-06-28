<div align="center">

# 🤖 AI RAG Assistant

**Template for AI-powered RAG assistant** — конвертируй Markdown в RAG и общайся через Web и MCP 🧠

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
![Status](https://img.shields.io/badge/Status-Development-yellow)

</div>

---

## 🚀 О проекте

Два компонента в одном репозитории:

| Компонент | Назначение |
|-----------|------------|
| `rag-generation/` | 🏗️ Скрипты на Python для подготовки/генерации RAG-базы из `.md` файлов |
| `assistant-container/` | 🐳 Docker-контейнер: Web UI + FastAPI + llama.cpp server + MCP |

### ✨ Фичи

- 🌐 **Web-форма** — человек задаёт вопрос → мини-модель → ответ из RAG
- 🤖 **MCP-интерфейс** — AI-агенты (opencode) получают знания через RAG
- 🔒 **Offline** — ни одного запроса в интернет при обработке знаний
- ⚙️ **Конфигурируемый** — гибкий `config` указывает папки с `.md` файлами

---

## 📁 Структура

```
ai-rag-assistent/
├── rag-generation/        # 🏗️ Генерация RAG-базы
│   ├── config             # 📋 какие папки сканировать
│   ├── src/               # ingest + chunking
│   ├── rag-generate.ps1   # 🪟 Windows
│   └── rag-generate.sh    # 🐧 Linux
├── assistant-container/   # 🐳 Docker-образ
│   ├── Dockerfile         # онлайн-сборка (llama-server + pip + next build)
│   ├── Dockerfile.offline # офлайн-сборка (multi-stage: llama-server + python + node)
│   ├── prepare-offline-bundle.ps1  # скачать бандл для офлайна
│   ├── docker-compose.yml
│   ├── backend/ + web/
│   ├── offline-bundle/    # предзагруженные артефакты
│   └── MIGRATE_TO_LLAMASERVER.md  # план миграции Ollama → llama.cpp
├── CONTRIBUTING.md        # 🤝 Как помочь проекту
└── LICENSE                # 📄 Apache 2.0
```

---

## 🏗️ Генерация RAG-базы

### 1. Подготовь Markdown-файлы

Создай файлы со знаниями в формате `.md`. Требования:

- используй заголовки `##` / `###` для разделения смысловых блоков
- одна секция = один чанк (до 1200 символов)
- без HTML-разметки внутри

Подробные правила — в [`rag-generation/docs/md-content-guidelines.md`](rag-generation/docs/md-content-guidelines.md).

Примеры готовых файлов: `rag-generation/docs/rules/` и `docs/poetry/`.

### 2. Настрой конфиг

Отредактируй [`rag-generation/config/rag-sources.yaml`](rag-generation/config/rag-sources.yaml) — укажи пути к папкам с `.md` файлами:

```yaml
sources:
  - name: rules
    path: ./docs/rules    # папка с твоими .md
```

### 3. Запусти генерацию

**Windows:**
```powershell
.\rag-generation\rag-generate.ps1
```

**Linux / macOS:**
```bash
bash rag-generation/rag-generate.sh
```

Скрипт проверит наличие Python, Git, создаст виртуальное окружение, установит зависимости и выполнит индексацию.

### 4. Проверь результат

После успешного запуска в `rag-generation/output/` появятся:

| Файл | Что это |
|------|---------|
| `chroma_db/` | 💾 Готовая векторная база ChromaDB |
| `manifest.json` | 📋 Манифест: количество чанков, источники |

Манифест выглядит так:
```json
{
  "total_chunks": 5,
  "sources": ["rules", "poetry"],
  "chunk_size": 1200,
  "overlap": 200
}
```

> База готова к использованию в `assistant-container` — она будет подмонтирована через Docker volume.

---

## 🔌 Настройка MCP для opencode

opencode использует MCP для доступа к RAG-базе знаний. 

### 🐳 Вариант через Docker (HTTP / SSE)

MCP сервер работает внутри контейнера на порту 8001. opencode подключается удалённо — не требует зависимостей на хосте.

**`.opencode.json`**:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "knowledge-rag": {
      "type": "remote",
      "url": "http://localhost:8001/sse",
      "enabled": true,
      "timeout": 30000
    }
  }
}
```

> Убедись, что в `docker-compose.yml` проброшен порт `8001:8001` и контейнер запущен.

После настройки можно прямо в opencode писать:
> "Найди в базе знаний правила кодирования"

---

## 📄 Лицензия

Распространяется под лицензией [Apache 2.0](LICENSE).
