# RAG Generator

Генерация ChromaDB-базы из `.md` файлов с помощью fastembed (ONNX, без torch).

## Быстрый старт

```powershell
# Собрать образ и запустить генерацию (вшитый config/rag-sources.yaml)
.\rag-build.ps1

# Только сборка
.\rag-build.ps1 -Build

# Запустить с внешними папками .md
.\rag-build.ps1 -Source c:\path\to\docs, c:\other\skills

# Запустить с кастомным конфигом (без пересборки образа)
.\rag-build.ps1 -Source c:\skills -Config .\my-sources.yaml

# Пересобрать с нуля и запустить
.\rag-build.ps1 -Build -Run

# Кастомный Docker-тег
.\rag-build.ps1 -Tag 2.0.0-rc1
```

## Параметры

| Параметр   | Описание |
|------------|----------|
| `-Build`   | Пересборка образа (`--no-cache`) |
| `-Run`     | Принудительный запуск генерации |
| `-Source`  | Внешние папки с `.md` файлами (монтируются в `/external/srcN`) |
| `-Config`  | Кастомный `rag-sources.yaml` вместо вшитого (монтируется без пересборки) |
| `-Tag`     | Docker-тег (по умолчанию из `VERSION`) |

## Docker Compose напрямую

```powershell
# Запустить со вшитым конфигом
docker compose up

# Запустить с кастомным конфигом (раскомментируй volume в docker-compose.yml)
docker compose up

# Собрать образ отдельно
docker compose build
```

После генерации результат в `output/chroma_db/` и `output/manifest.json`.

## Конфигурация

`rag-sources.yaml` описывает источники, чанкинг и модель эмбеддингов:

```yaml
sources:
  - name: rules
    path: ./docs/rules
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
  model: all-MiniLM-L6-v2
```

При использовании `-Source c:\docs` папки монтируются в `/external/src0`, `/external/src1` и т.д. — пути в yaml должны указывать на эти точки монтирования.

## Версионирование

Версия читается из `VERSION` и автоматически наносится на образ при сборке.
