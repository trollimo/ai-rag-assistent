"""Read-only view of the skill archives the generator built.

The assistant container has no source files of its own -- it only mounts
rag-generation/output/skills (chroma_db's sibling) read-only and serves what
it finds there. See rag-generation/docs/skills-architecture.md.
"""
import json
import logging
import re
from pathlib import Path

logger = logging.getLogger("backend.rag")

# Same shape the generator's skills.py enforces on skill folder names --
# re-checked here since index.json is technically an external input (a
# corrupted or tampered file shouldn't let a name walk the archive path
# outside the skills directory).
_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


class SkillsRegistry:
    def __init__(self, index_path: Path):
        self.index_path = index_path
        self._mtime = None
        self._skills: dict = {}
        self._load()

    def _load(self):
        try:
            mtime = self.index_path.stat().st_mtime
        except OSError:
            if self._skills:
                logger.warning("Skills index missing (%s), keeping last known list", self.index_path)
            else:
                logger.info("No skills index at %s -- skills feature inactive", self.index_path)
            return
        if mtime == self._mtime:
            return
        try:
            data = json.loads(self.index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            logger.error("Failed to read skills index %s: %s", self.index_path, e)
            return
        skills = {}
        for entry in data.get("skills", []):
            name = entry.get("name", "")
            if not _NAME_RE.match(name):
                logger.warning("Skipping skill with invalid name in index.json: %r", name)
                continue
            skills[name] = entry
        self._skills = skills
        self._mtime = mtime
        logger.info("Skills registry: %d skills from %s", len(skills), self.index_path)

    def list(self) -> list:
        self._load()  # cheap mtime check, picks up a fresh generator run without a restart
        return list(self._skills.values())

    def get(self, name: str):
        self._load()
        if not _NAME_RE.match(name):
            return None
        return self._skills.get(name)

    def archive_path(self, name: str):
        entry = self.get(name)
        if not entry:
            return None
        skills_dir = self.index_path.parent.resolve()
        path = (skills_dir / entry.get("archive", "")).resolve()
        if path.parent != skills_dir or not path.is_file():
            return None
        return path
