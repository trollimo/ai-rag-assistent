"""Queries for the feedback module.

Every public function here swallows database errors and returns a benign
value: callers sit on the /chat path or on a UI panel, and neither should
break because feedback storage is having a bad day.
"""
import json
import logging
import uuid

from sqlalchemy import text

from backend.core import settings
from backend.db import engine

logger = logging.getLogger("backend.db")


async def save_interaction(payload: dict) -> bool:
    """Insert one interaction. Idempotent on id (a reaction may race a log)."""
    if not engine.is_available():
        return False
    try:
        async with engine.session()() as s:
            await s.execute(
                text("""
                    INSERT INTO interactions (
                        id, question, normalized_query, answer, mode, answer_source,
                        sources, chunks, skills, client_id, channel, query_vector
                    ) VALUES (
                        :id, :question, :normalized_query, :answer, :mode, :answer_source,
                        CAST(:sources AS JSONB), CAST(:chunks AS JSONB), CAST(:skills AS JSONB),
                        :client_id, :channel, :query_vector
                    )
                    ON CONFLICT (id) DO NOTHING
                """),
                {
                    "id": payload["id"],
                    "question": payload["question"][: settings.FEEDBACK_MAX_TEXT],
                    "normalized_query": payload.get("normalized_query"),
                    "answer": payload["answer"][: settings.FEEDBACK_MAX_TEXT],
                    "mode": payload["mode"],
                    "answer_source": payload["answer_source"],
                    "sources": json.dumps(payload.get("sources", []), ensure_ascii=False),
                    "chunks": json.dumps(payload.get("chunks", []), ensure_ascii=False),
                    "skills": json.dumps(payload.get("skills", []), ensure_ascii=False),
                    "client_id": payload.get("client_id"),
                    "channel": payload.get("channel", "web"),
                    "query_vector": payload.get("query_vector"),
                },
            )
            await s.commit()
        return True
    except Exception as e:
        logger.warning("save_interaction failed: %s", e)
        return False


async def save_feedback(
    interaction_id: str | None,
    kind: str,
    comment: str | None,
    author: str | None,
    client_id: str | None,
) -> bool:
    """Record a reaction. up/down replace an earlier vote on the same answer."""
    if not engine.is_available():
        return False
    try:
        async with engine.session()() as s:
            if kind in ("up", "down") and interaction_id:
                # The partial unique index allows exactly one vote per answer,
                # so changing one's mind is a delete + insert, not a conflict.
                await s.execute(
                    text("""
                        DELETE FROM feedback
                        WHERE interaction_id = CAST(:iid AS UUID) AND kind IN ('up','down')
                    """),
                    {"iid": interaction_id},
                )
            await s.execute(
                text("""
                    INSERT INTO feedback (interaction_id, kind, comment, author, client_id)
                    VALUES (CAST(:iid AS UUID), :kind, :comment, :author, :client_id)
                """),
                {
                    "iid": interaction_id,
                    "kind": kind,
                    "comment": (comment or None) and comment[: settings.FEEDBACK_MAX_TEXT],
                    "author": author,
                    "client_id": client_id,
                },
            )
            await s.commit()
        return True
    except Exception as e:
        logger.warning("save_feedback failed: %s", e)
        return False


async def published_topics(limit: int = 100) -> list[dict]:
    """The public showcase: only titles that passed the publication gate."""
    if not engine.is_available():
        return []
    try:
        async with engine.session()() as s:
            rows = await s.execute(
                text("""
                    SELECT id, title, status, question_count, vote_count, resolution
                    FROM topics
                    WHERE status IN ('published', 'resolved')
                    ORDER BY vote_count DESC, question_count DESC, last_seen DESC
                    LIMIT :limit
                """),
                {"limit": limit},
            )
            return [dict(r._mapping) for r in rows]
    except Exception as e:
        logger.warning("published_topics failed: %s", e)
        return []


async def vote_topic(topic_id: int, client_id: str) -> int | None:
    """Add a vote and return the new count; None on failure.

    One vote per client_id per topic. localStorage is trivially cleared, so
    this is a de-duplicator for honest users rather than a security control
    -- acceptable for an internal prioritisation board.
    """
    if not engine.is_available():
        return None
    try:
        async with engine.session()() as s:
            await s.execute(
                text("""
                    INSERT INTO topic_votes (topic_id, client_id)
                    VALUES (:tid, :cid)
                    ON CONFLICT (topic_id, client_id) DO NOTHING
                """),
                {"tid": topic_id, "cid": client_id},
            )
            await s.execute(
                text("""
                    UPDATE topics SET vote_count =
                        (SELECT count(*) FROM topic_votes WHERE topic_id = :tid)
                    WHERE id = :tid
                """),
                {"tid": topic_id},
            )
            row = await s.execute(
                text("SELECT vote_count FROM topics WHERE id = :tid"), {"tid": topic_id}
            )
            await s.commit()
            value = row.scalar()
            return int(value) if value is not None else None
    except Exception as e:
        logger.warning("vote_topic failed: %s", e)
        return None


async def voted_topic_ids(client_id: str) -> list[int]:
    if not engine.is_available() or not client_id:
        return []
    try:
        async with engine.session()() as s:
            rows = await s.execute(
                text("SELECT topic_id FROM topic_votes WHERE client_id = :cid"),
                {"cid": client_id},
            )
            return [int(r[0]) for r in rows]
    except Exception as e:
        logger.warning("voted_topic_ids failed: %s", e)
        return []


# ── Clustering support ────────────────────────────────────────────

async def unclustered_gaps(limit: int = 500) -> list[dict]:
    """Interactions the knowledge base failed to answer, not yet in a topic."""
    if not engine.is_available():
        return []
    try:
        async with engine.session()() as s:
            rows = await s.execute(
                text("""
                    SELECT i.id, i.question, i.normalized_query, i.query_vector, i.client_id
                    FROM interactions i
                    LEFT JOIN topic_questions tq ON tq.interaction_id = i.id
                    WHERE tq.interaction_id IS NULL
                      AND i.query_vector IS NOT NULL
                    ORDER BY i.created_at DESC
                    LIMIT :limit
                """),
                {"limit": limit},
            )
            return [dict(r._mapping) for r in rows]
    except Exception as e:
        logger.warning("unclustered_gaps failed: %s", e)
        return []


async def existing_topics_with_centroids() -> list[dict]:
    if not engine.is_available():
        return []
    try:
        async with engine.session()() as s:
            rows = await s.execute(
                text("""
                    SELECT id, title, centroid, question_count
                    FROM topics
                    WHERE status <> 'hidden' AND centroid IS NOT NULL
                """)
            )
            return [dict(r._mapping) for r in rows]
    except Exception as e:
        logger.warning("existing_topics_with_centroids failed: %s", e)
        return []


async def create_topic(title: str, centroid: bytes) -> int | None:
    if not engine.is_available():
        return None
    try:
        async with engine.session()() as s:
            row = await s.execute(
                text("""
                    INSERT INTO topics (title, centroid, status)
                    VALUES (:title, :centroid, 'pending')
                    RETURNING id
                """),
                {"title": title, "centroid": centroid},
            )
            await s.commit()
            return int(row.scalar())
    except Exception as e:
        logger.warning("create_topic failed: %s", e)
        return None


async def attach_questions(topic_id: int, interaction_ids: list[str], centroid: bytes) -> None:
    """Link interactions to a topic, refresh its counters, and publish it if ready."""
    if not engine.is_available() or not interaction_ids:
        return
    try:
        async with engine.session()() as s:
            for iid in interaction_ids:
                await s.execute(
                    text("""
                        INSERT INTO topic_questions (topic_id, interaction_id)
                        VALUES (:tid, CAST(:iid AS UUID))
                        ON CONFLICT DO NOTHING
                    """),
                    {"tid": topic_id, "iid": str(iid)},
                )
            # A topic becomes public only once enough DISTINCT people have hit
            # it -- a one-off question is likelier to carry that person's own
            # pasted data than to represent a real gap.
            await s.execute(
                text("""
                    UPDATE topics t SET
                        centroid = :centroid,
                        last_seen = now(),
                        question_count = sub.cnt,
                        status = CASE
                            WHEN t.status = 'pending' AND sub.people >= :threshold THEN 'published'
                            ELSE t.status
                        END
                    FROM (
                        SELECT count(*) AS cnt,
                               count(DISTINCT i.client_id) AS people
                        FROM topic_questions tq
                        JOIN interactions i ON i.id = tq.interaction_id
                        WHERE tq.topic_id = :tid
                    ) sub
                    WHERE t.id = :tid
                """),
                {"tid": topic_id, "centroid": centroid,
                 "threshold": settings.FEEDBACK_PUBLISH_THRESHOLD},
            )
            await s.commit()
    except Exception as e:
        logger.warning("attach_questions failed: %s", e)


# ── Admin ─────────────────────────────────────────────────────────

async def admin_feedback(status: str | None, kind: str | None, limit: int = 200) -> list[dict]:
    if not engine.is_available():
        return []
    try:
        clauses, params = [], {"limit": limit}
        if status:
            clauses.append("f.status = :status")
            params["status"] = status
        if kind:
            clauses.append("f.kind = :kind")
            params["kind"] = kind
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        async with engine.session()() as s:
            rows = await s.execute(
                text(f"""
                    SELECT f.id, f.kind, f.comment, f.author, f.status, f.resolution,
                           f.created_at, f.interaction_id,
                           i.question, i.answer, i.answer_source, i.sources, i.chunks
                    FROM feedback f
                    LEFT JOIN interactions i ON i.id = f.interaction_id
                    {where}
                    ORDER BY f.created_at DESC
                    LIMIT :limit
                """),
                params,
            )
            return [dict(r._mapping) for r in rows]
    except Exception as e:
        logger.warning("admin_feedback failed: %s", e)
        return []


async def admin_topics(limit: int = 200) -> list[dict]:
    if not engine.is_available():
        return []
    try:
        async with engine.session()() as s:
            rows = await s.execute(
                text("""
                    SELECT id, title, status, question_count, vote_count,
                           first_seen, last_seen, resolution
                    FROM topics
                    ORDER BY vote_count DESC, question_count DESC
                    LIMIT :limit
                """),
                {"limit": limit},
            )
            return [dict(r._mapping) for r in rows]
    except Exception as e:
        logger.warning("admin_topics failed: %s", e)
        return []


async def update_feedback_status(fid: int, status: str, resolution: str | None) -> bool:
    if not engine.is_available():
        return False
    try:
        async with engine.session()() as s:
            await s.execute(
                text("UPDATE feedback SET status = :st, resolution = :res WHERE id = :id"),
                {"st": status, "res": resolution, "id": fid},
            )
            await s.commit()
        return True
    except Exception as e:
        logger.warning("update_feedback_status failed: %s", e)
        return False


async def update_topic(tid: int, status: str | None, title: str | None,
                       resolution: str | None) -> bool:
    if not engine.is_available():
        return False
    try:
        sets, params = [], {"id": tid}
        if status:
            sets.append("status = :status")
            params["status"] = status
        if title:
            sets.append("title = :title")
            params["title"] = title
        if resolution is not None:
            sets.append("resolution = :resolution")
            params["resolution"] = resolution
        if not sets:
            return True
        async with engine.session()() as s:
            await s.execute(text(f"UPDATE topics SET {', '.join(sets)} WHERE id = :id"), params)
            await s.commit()
        return True
    except Exception as e:
        logger.warning("update_topic failed: %s", e)
        return False


async def stats() -> dict:
    if not engine.is_available():
        return {}
    try:
        async with engine.session()() as s:
            row = await s.execute(text("""
                SELECT
                    (SELECT count(*) FROM interactions) AS interactions,
                    (SELECT count(*) FROM feedback WHERE kind = 'up') AS up,
                    (SELECT count(*) FROM feedback WHERE kind = 'down') AS down,
                    (SELECT count(*) FROM feedback WHERE kind = 'contribute') AS contribute,
                    (SELECT count(*) FROM interactions WHERE answer_source = 'no_info') AS no_info,
                    (SELECT count(*) FROM topics WHERE status = 'published') AS topics
            """))
            return dict(row.mappings().first() or {})
    except Exception as e:
        logger.warning("stats failed: %s", e)
        return {}


def new_id() -> str:
    return str(uuid.uuid4())
