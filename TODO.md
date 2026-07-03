# TODO

## Параметризовать embedding-модель

Сейчас название модели `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` хардкодом в:
- `rag-generation/src/embedding_fn.py`
- `assistant-container/backend/rag/embedding_fn.py`
- `rag-generation/Dockerfile`
- `assistant-container/Dockerfile`
- `assistant-container/Dockerfile.offline`
- `assistant-container/prepare-offline-bundle.ps1`

Вынести в `config/rag-sources.yaml` (для генератора) и `mcp-tools.yaml` (для сервиса). Тогда смена модели без пересборки образов.

## MCP timeout на другом ПК

### Логи (d:\temp\opencode-timeout.txt)

```
llama-server: 5.18s — inference OK (340 prompt + 18 eval токенов)
uvicorn (MCP port 9081):
  22:04:40 — POST /sse → 405 Method Not Allowed
  22:04:40 — GET  /sse → 200 OK
```

### Анализ

1. **POST /sse → 405** — клиент opencode сначала шлёт POST на `/sse`, получает 405, затем ретраится GET'ом и подключается. Это штатное поведение MCP-рукопожатия на некоторых реализациях клиента. На наш таймаут не влияет.

2. **Что может вызывать таймаут**:
   - На другом ПК в `.opencode.json` может быть неверный **URL** (порт 8001 вместо 9081, или `localhost` вместо реального IP сервера);
   - Файрволл/маршрутизация между ПК — проверить `Test-NetConnection <server_ip> -Port 9081`;
   - Опенкод на том ПК использует `type: "remote"` и коннектится через **HTTP SSE** — если между ПК есть прокси/VPN, SSE может рваться по таймауту;
   - В `.opencode.json` стоит `"timeout": 30000` (30с) — llama-server отвечает за 5с, `/search` за <1с. Должно хватать.

3. **Что проверить на том ПК**:
   - Содержимое `%USERPROFILE%\.config\opencode\opencode.json` — правильный ли URL и порт;
   - `curl http://<server_ip>:9081/sse` — открывается ли SSE-соединение;
   - `curl -X POST http://<server_ip>:8000/search -H "Content-Type: application/json" -d '{\"query\":\"test\",\"top_k\":1}'` — отвечает ли FastAPI.

### Решение (если подвердится)

- Если проблема в URL — поправить `.opencode.json` на том ПК.
- Если проблема в SSE через NAT/прокси — рассмотреть `stdio` транспорт вместо `remote` (через SSH-туннель или Docker exec).
