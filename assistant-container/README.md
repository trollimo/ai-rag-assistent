# RAG Assistant Container

## Быстрый старт

```powershell
# Запустить контейнер (сборка, если нет образа)
.\assistant-container\docker-run.ps1

# Остановить
.\assistant-container\docker-run.ps1 -Stop

# Перезапустить
.\assistant-container\docker-run.ps1 -Restart

# Логи
.\assistant-container\docker-run.ps1 -Logs

# Пересобрать с нуля
.\assistant-container\docker-run.ps1 -Build

# Собрать с кастомным тегом
.\assistant-container\docker-run.ps1 -Build -Tag 2.0.0-rc1
```

## Параметры

| Параметр | Описание |
|----------|----------|
| `-Build`   | Полная пересборка (`--no-cache`) |
| `-Logs`    | Подключиться к логам (`docker logs -f`) |
| `-Stop`    | Остановить и удалить контейнер |
| `-Restart` | Перезапустить контейнер |
| `-Tag`     | Кастомный Docker-тег (по умолчанию из VERSION) |

## Версионирование

Версия читается из `VERSION` и автоматически наносится на образ при сборке.
Для ручного тегирования:

```powershell
.\docker-run.ps1 -Build -Tag 1.0.0
```

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

После этого opencode получит инструменты `search_docs` и `list_topics` — поиск по RAG-базе и список тем.
Описание инструментов (docstring, по которому LLM решает вызывать их) задаётся в файле `backend/config/mcp-tools.yaml`. Можешь отредактировать его под свои источники знаний — правки применяются после перезапуска контейнера.
```
