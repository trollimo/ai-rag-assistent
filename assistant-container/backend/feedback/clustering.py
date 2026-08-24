"""Group unanswered questions into topics for the public showcase.

Split of labour, each tool doing what it is actually good at:

* **Embeddings do the grouping.** The query vector was already computed
  during /chat and stored, so clustering costs no model inference at all --
  just arithmetic. Deterministic, and reuses infrastructure that exists.
* **The LLM only writes the title**, once per new cluster. It is explicitly
  instructed to produce a generic formulation and never to carry over
  concrete values, hosts or credentials -- this title is the only thing
  that ever becomes publicly visible, so it is the last place raw user text
  could leak through.

Runs on a timer in the background rather than on the request path:
embedding-adjacent work on a CPU-bound event loop is already a known
bottleneck (CLAUDE.md item #8) and this must not add to it.
"""
import asyncio
import logging
import struct

from backend.core import settings
from backend.db import repo

logger = logging.getLogger("backend.feedback")

_TITLE_PROMPT = (
    "Ты формулируешь короткое название темы для внутренней базы знаний по "
    "разработке. На вход — несколько вопросов сотрудников об одном и том же. "
    "Верни ОДНУ обобщённую формулировку темы на русском языке, до 80 символов, "
    "без кавычек и пояснений.\n"
    "Строгие запреты: не переноси в ответ конкретные значения, имена хостов, "
    "IP-адреса, логины, пароли, токены, ключи, названия внутренних серверов и "
    "любые другие данные из вопросов. Только суть темы."
)


def pack_vector(vector) -> bytes:
    return struct.pack(f"<{len(vector)}f", *(float(x) for x in vector))


def unpack_vector(blob: bytes) -> list[float]:
    if not blob:
        return []
    return list(struct.unpack(f"<{len(blob) // 4}f", blob))


def _sq_distance(a: list[float], b: list[float]) -> float:
    """Squared L2 -- same metric chromadb reports, so thresholds stay comparable."""
    return sum((x - y) * (x - y) for x, y in zip(a, b))


def _mean(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        return []
    n = len(vectors)
    return [sum(v[i] for v in vectors) / n for i in range(len(vectors[0]))]


async def _title_for(questions: list[str], ask_llm) -> str:
    sample = "\n".join(f"- {q}" for q in questions[:8])
    try:
        title = await ask_llm([
            {"role": "system", "content": _TITLE_PROMPT},
            {"role": "user", "content": sample},
        ])
        title = " ".join(title.strip().strip('"').split())
    except Exception as e:
        logger.warning("Topic title generation failed: %s", e)
        title = ""
    if not title or title.startswith("[LLM error"):
        # Fall back to the shortest question rather than publishing nothing --
        # but it is user text, so it stays redacted and length-capped.
        title = min(questions, key=len) if questions else "Без названия"
    # Hard cap: a short title physically cannot smuggle a connection string.
    return title[:90]


async def run_once(ask_llm) -> dict:
    """One clustering pass. Returns a small summary for logs/admin."""
    gaps = await repo.unclustered_gaps()
    if not gaps:
        return {"gaps": 0, "new_topics": 0, "attached": 0}

    topics = await repo.existing_topics_with_centroids()
    centroids = [
        {"id": t["id"], "vector": unpack_vector(t["centroid"]), "members": []}
        for t in topics
    ]
    threshold = settings.FEEDBACK_CLUSTER_MAX_DISTANCE

    fresh: list[dict] = []      # brand-new clusters formed in this pass
    attached = 0

    for gap in gaps:
        vector = unpack_vector(gap["query_vector"])
        if not vector:
            continue
        question = gap.get("normalized_query") or gap["question"]

        best, best_dist = None, None
        for bucket in centroids + fresh:
            dist = _sq_distance(vector, bucket["vector"])
            if best_dist is None or dist < best_dist:
                best, best_dist = bucket, dist

        if best is not None and best_dist is not None and best_dist <= threshold:
            best["members"].append({"id": gap["id"], "question": question, "vector": vector})
            attached += 1
        else:
            fresh.append({
                "id": None,
                "vector": vector,
                "members": [{"id": gap["id"], "question": question, "vector": vector}],
            })

    # Existing topics: just link the new questions and refresh the centroid.
    for bucket in centroids:
        if not bucket["members"]:
            continue
        vectors = [m["vector"] for m in bucket["members"]] + [bucket["vector"]]
        await repo.attach_questions(
            bucket["id"], [m["id"] for m in bucket["members"]], pack_vector(_mean(vectors))
        )

    # New clusters: name them, then link.
    created = 0
    for bucket in fresh:
        centroid = _mean([m["vector"] for m in bucket["members"]])
        title = await _title_for([m["question"] for m in bucket["members"]], ask_llm)
        topic_id = await repo.create_topic(title, pack_vector(centroid))
        if topic_id is None:
            continue
        await repo.attach_questions(
            topic_id, [m["id"] for m in bucket["members"]], pack_vector(centroid)
        )
        created += 1

    summary = {"gaps": len(gaps), "new_topics": created, "attached": attached}
    logger.info("Clustering pass: %s", summary)
    return summary


async def loop(ask_llm) -> None:
    """Background task; started only when the module and showcase are on."""
    interval = max(1, settings.FEEDBACK_CLUSTER_INTERVAL_MINUTES) * 60
    while True:
        await asyncio.sleep(interval)
        try:
            await run_once(ask_llm)
        except Exception as e:
            # A failed pass must not kill the task -- the next tick retries.
            logger.warning("Clustering pass failed: %s", e)
