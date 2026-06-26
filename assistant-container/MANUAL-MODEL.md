# Manual Phi4-Mini Model Download (offline/closed network)

Если Docker не может скачать `phi4-mini` (нет доступа к интернету из Docker),
но у вас есть **браузер** на этой же машине — вот как подложить модель вручную.

## Способ 1: GGUF + Modelfile (рекомендуется)

### Шаг 1. Скачать GGUF через браузер

Зайти на HuggingFace и скачать 4-бит квантованный GGUF:

- **https://huggingface.co/bartowski/phi-4-mini-instruct-GGUF**
- Файл: `phi-4-mini-instruct-Q4_K_M.gguf` (~2.5 GB)
- Положить в: `assistant-container/models/phi-4-mini-instruct-Q4_K_M.gguf`

### Шаг 2. Создать Modelfile

`assistant-container/models/Modelfile`:
```
FROM /app/models/phi-4-mini-instruct-Q4_K_M.gguf
```

### Шаг 3. Альтернативный Dockerfile (без downloader стейджа)

`assistant-container/Dockerfile.offline`:
```dockerfile
FROM ollama/ollama:latest

ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_MODELS=/root/.ollama/models

COPY models/phi-4-mini-instruct-Q4_K_M.gguf /app/models/phi-4-mini-instruct-Q4_K_M.gguf
COPY models/Modelfile /app/models/Modelfile

# Импортируем модель при старте (однократно)
RUN ollama serve & sleep 3 && ollama create phi4-mini -f /app/models/Modelfile && ollama stop || true

# --- далее всё как в основном Dockerfile ---
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv nodejs npm && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip3 install --no-cache-dir -r /app/backend/requirements.txt

RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY backend /app/backend
COPY web /app/web

RUN cd /app/web && npm install && npm run build

EXPOSE 11434 8000 3000

CMD ["sh", "-c", "ollama serve & uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 & cd /app/web && npm run start -p 3000"]
```

### Шаг 4. Собрать

```powershell
docker compose -f docker-compose.yml build --build-arg MODEL_SOURCE=offline
```

Либо просто заменить `Dockerfile` на `Dockerfile.offline` в `docker-compose.yml`.

---

## Способ 2: Готовая папка `.ollama` с другого компьютера

Если есть машина **с интернетом**, на которой стоит Ollama:

```bash
ollama pull phi4-mini
```

Найти, куда сохранилось:
```bash
ollama show phi4-mini --modelfile
# Или просто: ls ~/.ollama/models/
```

Скопировать всё содержимое `~/.ollama/models/` (blobs + manifests).

Перенести через браузер (флешка / корпоративный облачный диск) в:

```
assistant-container/models/ollama_models/
   blobs/
   manifests/
```

Изменить Dockerfile — стейдж `downloader` заменить на:

```dockerfile
FROM ollama/ollama:latest as downloader
COPY models/ollama_models /root/.ollama/models
```

---

## Как скачать GGUF через браузер (подробно)

1. Открыть https://huggingface.co/bartowski/phi-4-mini-instruct-GGUF
2. Нажать `Files and versions`
3. Найти `phi-4-mini-instruct-Q4_K_M.gguf`
4. Клик правой кнопкой → Save link as / Сохранить как
5. Сохранить в `D:\git2\ai-rag-assistent\assistant-container\models\`

Размер: ~2.5 GB, дольше всего скачивается именно этот файл.

---

## Сравнение подходов

| Способ | Сложность | Размер | Надёжность |
|--------|-----------|--------|------------|
| GGUF + Modelfile | Низкая | 2.5 GB | Высокая |
| Готовая .ollama папка | Средняя | ~3 GB | Высокая |
| Оригинальный Dockerfile (через gerke74) | Не работает в closed net | 0 | Недоступен |
