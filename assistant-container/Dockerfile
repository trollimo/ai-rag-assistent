FROM gerke74/ollama-model-loader:latest as downloader
RUN /ollama-pull phi4-mini

FROM ollama/ollama:latest

ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_MODELS=/root/.ollama/models

COPY --from=downloader /root/.ollama /root/.ollama

RUN apt-get update && apt-get install -y python3 python3-pip python3-venv nodejs npm && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Offline wheels (prepared by prepare-offline-bundle.ps1)
COPY offline-bundle/wheels /app/wheels
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip3 install --break-system-packages --no-index --find-links /app/wheels -r /app/backend/requirements.txt

# Offline HuggingFace cache (sentence-transformers model)
COPY offline-bundle/hf-cache /root/.cache/huggingface

COPY backend /app/backend
COPY web /app/web

# Offline node_modules (prepared by prepare-offline-bundle.ps1)
COPY offline-bundle/node_modules /app/web/node_modules
RUN cd /app/web && npm run build

EXPOSE 11434 8000 3000

CMD ["sh", "-c", "ollama serve & uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 & cd /app/web && npm run start -p 3000"]
