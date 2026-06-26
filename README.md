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
| `assistent-container/` | 🐳 Docker-контейнер с Web-интерфейсом и MCP-сервером для AI-агентов |

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
│   ├── rag-generate.ps1   # 🪟 Windows
│   └── rag-generate.sh    # 🐧 Linux
├── assistent-container/   # 🐳 Docker-образ
│   ├── docker-compose.yml
│   └── ...
├── CONTRIBUTING.md        # 🤝 Как помочь проекту
└── LICENSE                # 📄 Apache 2.0
```

---

## 🛠️ Разработка

> Проект в активной разработке. Структура может меняться.

```bash
git clone https://github.com/trollimo/ai-rag-assistent
cd ai-rag-assistent
```

Подробнее — в [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 Лицензия

Распространяется под лицензией [Apache 2.0](LICENSE).
