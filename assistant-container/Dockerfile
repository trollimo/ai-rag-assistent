FROM gerke74/ollama-model-loader:latest as downloader
RUN /ollama-pull phi4-mini

FROM ollama/ollama:latest

ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_MODELS=/root/.ollama/models

COPY --from=downloader /root/.ollama /root/.ollama

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
