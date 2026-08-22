# RAG Assistant Container

Архивариус — Web UI + FastAPI + MCP-сервер поверх RAG-базы, собранной
`rag-generation`. Два сервиса в `docker-compose.yml`: `assistant` (этот
контейнер) и `llm` (локальный llama-server; можно не запускать и указать
внешний OpenAI-совместимый эндпоинт через `LLM_BASE_URL`).

## Быстрый старт

```powershell
# Запустить (соберёт образ, если его нет)
.\docker-run.ps1

# Пересобрать код и перезапустить (использует кеш слоёв)
.\docker-run.ps1 -Build

# Полная пересборка без кеша (редко нужно — минуты на fastembed-cache/pip)
.\docker-run.ps1 -Build -NoCache

# Пересоздать контейнеры без пересборки — подхватить .env/compose правки
.\docker-run.ps1 -Rerun

# Остановить
.\docker-run.ps1 -Stop

# Логи (можно ограничить сервисом)
.\docker-run.ps1 -Logs -Service assistant
```

Правки в `backend/` подхватываются без пересборки — папка примонтирована
volume'ом. Правки в `web/` требуют пересборки бандла: `prepare-offline-bundle.ps1`
(npm build) → `docker-run.ps1 -Build`.

## Параметры

| Параметр   | Описание |
|------------|----------|
| `-Build`   | Пересобрать образ(а) (использует кеш слоёв) |
| `-NoCache` | С `-Build`: игнорировать кеш (пересобирает fastembed-cache/pip заново) |
| `-Rerun`   | `down` + `up` — пересоздать контейнеры, подхватив compose/.env |
| `-Stop`    | Остановить и удалить контейнеры |
| `-Logs`    | Подключиться к логам (`docker compose logs -f`) |
| `-Service` | Ограничить действие одним сервисом (`assistant` или `llm`) |

## Версионирование

Версия читается из `VERSION`; тег образа задаётся вручную в `docker-compose.yml`
(`image: rag-offline:X.Y.Z`) — при любом изменении содержимого образа версию
нужно поднять, образ пересобрать и тег в compose обновить, иначе он продолжит
указывать на старый образ.

## Ссылки

| Сервис | URL |
|--------|-----|
| Web UI    | http://localhost:3000 |
| API       | http://localhost:8000 |
| MCP (Streamable HTTP) | http://localhost:9081/mcp |
| MCP SSE (альтернатива) | http://localhost:9081/sse |
| LLM API (OpenAI-формат) | http://localhost:9080 |
| llama-server Web UI    | http://localhost:9080 |

## Использование

У контейнера **два веб-интерфейса** для общения.

### 1. RAG Web UI — http://localhost:3000

Next.js чат со **встроенным RAG**. Отправляет вопрос → `/chat` (FastAPI) → поиск в ChromaDB → контекст + вопрос → LLM → ответ.
Подходит для обычного Q&A по документации. MCP не требуется.

### 2. llama-server Web UI — http://localhost:9080

Встроенный чат llama.cpp с поддержкой **MCP-инструментов**.
Чтобы подключить RAG-базу знаний:

1. Открой `http://localhost:9080/#/mcp-servers`
2. Добавь сервер:
   - URL: `http://localhost:9081/mcp`
   - "Use llama-server proxy": **включено** (галочка)
3. В чате модель сможет вызывать `search_docs` и `list_topics`

Подходит для отладки и работы напрямую через llama-server без Next.js.

## Структура

```
backend/          # FastAPI + MCP + RAG
web/              # Next.js
Dockerfile        # online (модель качается с HF)
Dockerfile.offline # offline (из offline-bundle/)
docker-compose.yml
VERSION
```

## Скиллы

Ассистент не хранит исходники скиллов — только read-only монтирует то, что
собрал генератор (`rag-generation/output/skills`), и раздаёт:

| Что | Где |
|---|---|
| Каталог скиллов | `GET /skills` |
| Карточка (файлы, инструкция установки) | `GET /skills/{name}` |
| Сам архив | `GET /skills/{name}/archive` |
| Вкладка в Web UI | «Skills» вверху правой панели |
| MCP-инструменты | `list_skills`, `get_skill` |

Агент (например OpenCode) получает от `get_skill` не сам архив, а
`download_url` + `sha256` + готовую команду установки — и качает/распаковывает
сам через свои bash/файловые инструменты. Ссылка собирается из переменной
`PUBLIC_BASE_URL` (адрес, по которому контейнер виден агенту — не `localhost`,
если агент работает не на этой же машине).

Полная архитектура фичи (что попадает в RAG, а что в архив, детекция скиллов,
почему так) — в [`rag-generation/docs/skills-architecture.md`](../rag-generation/docs/skills-architecture.md).
Как добавить новый скилл — в [`rag-generation/README.md`](../rag-generation/README.md#скиллы-installable-skills).

## Opencode Integration

Для подключения opencode к MCP-серверу создай в корне проекта `.opencode.json`:

### Streamable HTTP (рекомендуется)

```json
{
  "mcp_servers": {
    "knowledge": {
      "type": "remote",
      "url": "http://localhost:9081/mcp"
    }
  }
}
```

### SSE (альтернатива)

```json
{
  "mcp_servers": {
    "knowledge": {
      "type": "remote",
      "url": "http://localhost:9081/sse"
    }
  }
}
```

После этого opencode получит инструменты `search_docs`, `list_topics`,
`list_skills` и `get_skill` — поиск по RAG-базе, список тем и работу со
скиллами. Описание инструментов (docstring, по которому LLM решает вызывать
их) задаётся в файле `backend/config/mcp-tools.yaml`. Можешь отредактировать
его под свои источники знаний — правки применяются после перезапуска
контейнера (или сразу, если volume с этим файлом раскомментирован в
`docker-compose.yml`).
