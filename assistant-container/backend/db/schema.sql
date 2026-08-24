-- Feedback module schema. Applied idempotently at startup (see engine.py):
-- no migration tool on purpose, the offline/closed-network deployment story
-- is simpler with plain CREATE ... IF NOT EXISTS than with alembic.
--
-- This is the only non-rebuildable data in the system: chroma_db and the
-- skill archives regenerate from Bitbucket in minutes, human feedback does
-- not. Hence a real database with a real pg_dump story.

CREATE TABLE IF NOT EXISTS interactions (
    id               UUID PRIMARY KEY,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    question         TEXT        NOT NULL,   -- already redacted, see core/redaction.py
    normalized_query TEXT,
    answer           TEXT        NOT NULL,
    mode             TEXT        NOT NULL,
    answer_source    TEXT        NOT NULL,   -- rag | llm_knowledge | no_info
    sources          JSONB       NOT NULL DEFAULT '[]',
    chunks           JSONB       NOT NULL DEFAULT '[]',  -- [{id, distance}] -- the "vector" link
    skills           JSONB       NOT NULL DEFAULT '[]',
    client_id        TEXT,
    channel          TEXT        NOT NULL DEFAULT 'web',
    -- Only stored for interactions that are candidates for the showcase
    -- (nothing found). 4 KB per row of float32 adds up fast otherwise, and
    -- answered questions are never clustered.
    query_vector     BYTEA
);

CREATE INDEX IF NOT EXISTS interactions_gaps
    ON interactions (answer_source, created_at DESC);

CREATE TABLE IF NOT EXISTS feedback (
    id             BIGSERIAL PRIMARY KEY,
    -- Nullable: if someone reacts after the in-memory cache dropped the
    -- interaction, the typed comment is still worth more than the context
    -- it lost. Such rows show up as "контекст утерян" in the admin view.
    interaction_id UUID        REFERENCES interactions(id) ON DELETE CASCADE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    kind           TEXT        NOT NULL,     -- up | down | contribute
    comment        TEXT,
    author         TEXT,
    client_id      TEXT,
    status         TEXT        NOT NULL DEFAULT 'new',  -- new|reviewed|actioned|rejected
    resolution     TEXT
);

-- One vote per answer; "знаю больше" can be submitted repeatedly.
CREATE UNIQUE INDEX IF NOT EXISTS feedback_one_vote
    ON feedback (interaction_id) WHERE kind IN ('up', 'down');

CREATE INDEX IF NOT EXISTS feedback_triage
    ON feedback (status, created_at DESC);

CREATE TABLE IF NOT EXISTS topics (
    id             BIGSERIAL PRIMARY KEY,
    title          TEXT        NOT NULL,     -- LLM-written, generic, public
    status         TEXT        NOT NULL DEFAULT 'pending',  -- pending|published|hidden|resolved
    question_count INT         NOT NULL DEFAULT 0,
    vote_count     INT         NOT NULL DEFAULT 0,
    centroid       BYTEA,
    first_seen     TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen      TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolution     TEXT
);

CREATE INDEX IF NOT EXISTS topics_public
    ON topics (status, vote_count DESC, question_count DESC);

CREATE TABLE IF NOT EXISTS topic_questions (
    topic_id       BIGINT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    interaction_id UUID   NOT NULL REFERENCES interactions(id) ON DELETE CASCADE,
    PRIMARY KEY (topic_id, interaction_id)
);

CREATE TABLE IF NOT EXISTS topic_votes (
    topic_id   BIGINT      NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    client_id  TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (topic_id, client_id)
);
