"""Database connection for the feedback module, with hard graceful degradation.

Two invariants this file exists to guarantee:

1. When `feedback.enabled` is false, nothing here is ever imported into a
   working state -- no engine, no connection attempt, no dependency on
   Postgres being present at all.
2. When it is enabled but the database is unreachable, /chat still answers.
   The entrypoint runs the API under `wait -n`, so an unhandled exception
   that kills the process takes the whole container down with it -- an
   unavailable feedback database must never escalate into "the assistant is
   down".
"""
import asyncio
import logging
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from backend.core import settings

logger = logging.getLogger("backend.db")

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker | None = None
_available = False


def is_available() -> bool:
    """True only if the module is switched on AND the schema is ready."""
    return _available


async def init_with_retry(attempts: int = 30, delay_seconds: float = 2.0) -> None:
    """Keep trying to connect in the background until the database shows up.

    Necessary because the assistant deliberately has no `depends_on` for the
    feedback database, so `docker compose up` regularly starts it before
    Postgres is accepting connections. Without a retry the module would stay
    dead until someone restarted the container -- the race would silently
    decide whether the feature works.
    """
    if not settings.FEEDBACK_ENABLED:
        logger.info("Feedback module disabled (feedback.enabled=false) -- no database used")
        return
    for attempt in range(1, attempts + 1):
        if await init(quiet=attempt < attempts):
            return
        await asyncio.sleep(delay_seconds)
    logger.error(
        "Feedback database still unreachable after %d attempts -- the assistant "
        "keeps working, feedback will not be stored", attempts,
    )


async def init(quiet: bool = False) -> bool:
    """Connect and apply the schema. Never raises -- logs and stays disabled."""
    global _engine, _sessionmaker, _available

    if not settings.FEEDBACK_ENABLED:
        logger.info("Feedback module disabled (feedback.enabled=false) -- no database used")
        return False

    try:
        _engine = create_async_engine(
            settings.FEEDBACK_DB_URL,
            pool_size=5,
            max_overflow=5,
            pool_pre_ping=True,   # a restarted Postgres shouldn't poison pooled connections
            future=True,
        )
        schema = (Path(__file__).resolve().parent / "schema.sql").read_text(encoding="utf-8")
        async with _engine.begin() as conn:
            for statement in _split_statements(schema):
                await conn.execute(text(statement))
        _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)
        _available = True
        logger.info("Feedback database ready: %s", _mask_url(settings.FEEDBACK_DB_URL))
        return True
    except Exception as e:
        _available = False
        if _engine is not None:
            # Otherwise a half-built engine leaks a connection pool per retry.
            try:
                await _engine.dispose()
            except Exception:
                pass
            _engine = None
        if quiet:
            logger.debug("Feedback database not ready yet: %s", e)
        else:
            logger.error(
                "Feedback database unavailable (%s) -- the assistant keeps working, "
                "feedback will not be stored", e,
            )
        return False


async def dispose() -> None:
    global _available
    _available = False
    if _engine is not None:
        await _engine.dispose()


def _split_statements(sql: str) -> list[str]:
    """Split schema.sql into statements, ignoring semicolons inside comments.

    Splitting the raw text on ';' looks safe for a file we control -- until a
    prose comment contains one ("-- One vote per answer; ..."), which cuts the
    comment in half and hands the tail to the server as SQL. Strip line
    comments first, then split.
    """
    stripped = "\n".join(
        line.split("--", 1)[0] if "--" in line else line
        for line in sql.splitlines()
    )
    return [s.strip() for s in stripped.split(";") if s.strip()]


def session() -> async_sessionmaker:
    if _sessionmaker is None:
        raise RuntimeError("Feedback database is not initialised")
    return _sessionmaker


def _mask_url(url: str) -> str:
    """Never log the password, even at INFO on a private network."""
    if "@" not in url:
        return url
    head, tail = url.rsplit("@", 1)
    if ":" in head:
        scheme_user = head.rsplit(":", 1)[0]
        return f"{scheme_user}:***@{tail}"
    return f"{head}@{tail}"
