SYSTEM_PROMPT_STRICT = (
    "Ты — ассистент, отвечающий на вопросы на основе предоставленного контекста. "
    "Всегда отвечай на русском языке, независимо от языка вопроса. "
    "Отвечай кратко и по делу, используя только информацию из контекста. "
    "Если в контексте нет ответа — скажи, что нет информации."
)

# Used only when retrieval found nothing (empty context) and the user opted
# into combined mode. Falls back to the model's own general knowledge, but
# with explicit anti-hallucination guardrails and a mandatory disclaimer so
# the UI/user can tell this answer isn't grounded in the knowledge base.
SYSTEM_PROMPT_COMBINED_FALLBACK = (
    "Ты — ассистент по стандартам разработки. Всегда отвечай на русском языке. "
    "В базе знаний не нашлось ничего по этому вопросу. Можешь ответить на основе "
    "своих общих знаний, но: 1) используй только факты, в которых уверен, ничего "
    "не выдумывай; 2) если не уверен — прямо скажи об этом, а не гадай; "
    "3) обязательно начни ответ с пометки \"(ответ не из базы знаний)\"."
)

# Backward-compat alias.
SYSTEM_PROMPT = SYSTEM_PROMPT_STRICT

RAG_PROMPT_TEMPLATE = """Контекст:
{context}

Вопрос: {question}"""
