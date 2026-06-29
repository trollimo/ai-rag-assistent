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
| MCP SSE   | http://localhost:9081/sse |
| LLM API   | http://localhost:9080 |

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

После этого opencode получит инструмент `search_docs` — поиск по RAG-базе.
Описание инструмента (docstring, по которому LLM решает вызывать его) задаётся в файле `backend/config/mcp-tools.yaml`. Можешь отредактировать его под свои источники знаний — правки применяются после перезапуска контейнера.
```
