"""Skill detection, metadata parsing, and archive building.

A "skill" is any immediate subfolder of a `type: skills` source that contains
a SKILL.md. Two derived artifacts come out of it: chunks (only the .md files,
for RAG) and a zip archive (the whole folder minus `archive.exclude`, for
installing into a code agent). See rag-generation/docs/skills-architecture.md
for the full design.
"""
import fnmatch
import hashlib
import re
import zipfile
from pathlib import Path

import yaml

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_VERSION_RE = re.compile(r"^Version:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
_HEADING_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_DIR_EXCLUDE_RE = re.compile(r"^\*\*/(.+)/\*\*$")


def find_skill_roots(source_dir: Path) -> list:
    """Immediate subfolders of source_dir containing a SKILL.md.

    Nested skills (a SKILL.md deeper than one level) are not searched for --
    the first match wins, we don't recurse past it.
    """
    if not source_dir.exists():
        return []
    return sorted(
        child for child in source_dir.iterdir()
        if child.is_dir() and (child / "SKILL.md").exists()
    )


def parse_skill_metadata(skill_root: Path) -> dict:
    """Read SKILL.md, tolerant of skills with no YAML frontmatter at all.

    Real-world skills don't reliably follow the Claude Code frontmatter
    convention -- trollimo/java-performance-review-skill, for example, has
    none, just a title and a plain "Version: 1.0 MVP" line. Falls back to
    the first heading / first real paragraph / a Version: line when
    frontmatter is missing or incomplete.
    """
    text = (skill_root / "SKILL.md").read_text(encoding="utf-8-sig")
    name = skill_root.name

    frontmatter = {}
    m = _FRONTMATTER_RE.match(text)
    if m:
        try:
            frontmatter = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            frontmatter = {}

    # The H1 heading is the human-friendly display title; frontmatter's
    # "name" (when present) is a slug-like identifier per the Claude Code
    # skill convention, not meant for display -- only fall back to it.
    title = _first_heading(text) or frontmatter.get("name") or name
    description = frontmatter.get("description") or _first_paragraph(text) or ""
    version = str(frontmatter.get("version") or _find_version(text) or "")

    return {
        "name": name,  # folder name is always the primary key, never from content
        "title": title,
        "description": description.strip(),
        "version": version,
    }


def _first_heading(text: str):
    m = _HEADING_RE.search(text)
    return m.group(1).strip() if m else None


def _first_paragraph(text: str):
    # Skip the title heading, then the first real prose block -- not a
    # "Version: ..." line, not a "---" rule, not another heading.
    body = _HEADING_RE.sub("", text, count=1)
    for para in re.split(r"\n\s*\n", body):
        para = para.strip()
        if not para or para.startswith("#") or _VERSION_RE.match(para) or set(para) <= {"-"}:
            continue
        return " ".join(para.split())[:400]
    return None


def _find_version(text: str):
    m = _VERSION_RE.search(text)
    return m.group(1).strip() if m else None


def _is_excluded(rel_path: str, exclude_patterns: list) -> bool:
    parts = rel_path.split("/")
    for pat in exclude_patterns:
        # Common shape "**/<name>/**" -- treat <name> as an excluded
        # directory component at any depth, not just where fnmatch's
        # "*" (which already spans "/") happens to line up.
        dm = _DIR_EXCLUDE_RE.match(pat)
        if dm and dm.group(1) in parts[:-1]:
            return True
        if fnmatch.fnmatch(rel_path, pat):
            return True
    return False


def build_skill_archive(skill_root: Path, exclude_patterns: list, max_size_mb: float, dest_zip: Path) -> dict:
    """Zip the whole skill folder (minus exclude_patterns) with paths
    relative to skill_root, so SKILL.md lands at the archive's own root --
    ready to unzip straight into ~/.config/opencode/skills/<name>/.

    Returns {"files": [...], "size_bytes": int, "sha256": str}. The hash is
    over file contents, not the zip bytes -- zip isn't byte-reproducible
    (timestamps), and this lets a caller detect "unchanged" without
    re-zipping.
    """
    files = []
    for p in sorted(skill_root.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(skill_root).as_posix()
        if _is_excluded(rel, exclude_patterns):
            continue
        files.append((p, rel))

    total_size = sum(p.stat().st_size for p, _ in files)
    max_bytes = max_size_mb * 1024 * 1024
    if total_size > max_bytes:
        raise ValueError(
            f"Skill '{skill_root.name}' is {total_size / 1024 / 1024:.1f} MB, "
            f"over the {max_size_mb} MB archive limit (archive.max_size_mb)"
        )

    content_hash = hashlib.sha256()
    for p, rel in files:
        content_hash.update(rel.encode("utf-8"))
        content_hash.update(p.read_bytes())
    sha256 = content_hash.hexdigest()

    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for p, rel in files:
            # Fixed timestamp: keeps the zip byte-identical across runs when
            # content hasn't changed, so callers can skip rewriting it.
            zi = zipfile.ZipInfo(rel, date_time=(2020, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(zi, p.read_bytes())

    return {
        "files": [rel for _, rel in files],
        "size_bytes": total_size,
        "sha256": sha256,
    }
