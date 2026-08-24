"""Generate synthetic .md files to reproduce the ~600-chunk slow-indexing scenario.

Usage: python gen_synthetic_docs.py [out_dir] [num_files] [sections_per_file]

Each section is ~1000 chars under its own `##` header, which chunking.py
turns into exactly one chunk (between the 800-char merge floor and the
1200-char split ceiling), so file_count * sections_per_file ~= chunk count.
"""
import random
import sys
from pathlib import Path

WORDS = (
    "под контейнер образ реплика деплоймент namespace сервис ingress маршрутизация "
    "балансировка нагрузка манифест helm chart values шаблон релиз откат revision "
    "конфигмап секрет volume persistentvolume claim ноды кластер scheduler kubelet "
    "readiness liveness probe healthcheck rollout масштабирование autoscaler hpa"
).split()

TOPICS = [
    "Deployment", "Pod", "Service", "Ingress", "Helm Chart", "ConfigMap",
    "Secret", "StatefulSet", "Namespace", "Autoscaling", "Rollout", "Networking",
    "PersistentVolume",
]


def make_paragraph(rng: random.Random, target_len: int) -> str:
    words = []
    length = 0
    while length < target_len:
        w = rng.choice(WORDS)
        words.append(w)
        length += len(w) + 1
    return " ".join(words).capitalize() + "."


def make_section(rng: random.Random, topic: str, idx: int) -> str:
    header = f"## Kubernetes {topic}: практика {idx}\n\n"
    body = make_paragraph(rng, 950)
    return header + body + "\n\n"


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "docs" / "synthetic"
    num_files = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    sections_per_file = int(sys.argv[3]) if len(sys.argv) > 3 else 20

    rng = random.Random(42)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.md"):
        old.unlink()

    total_sections = 0
    for i in range(num_files):
        topic = TOPICS[i % len(TOPICS)]
        lines = [f"# Kubernetes: {topic} — руководство {i}\n\n"]
        for j in range(sections_per_file):
            lines.append(make_section(rng, topic, j))
            total_sections += 1
        (out_dir / f"synthetic-{i:03d}.md").write_text("".join(lines), encoding="utf-8")

    print(f"Generated {num_files} files, ~{total_sections} sections in {out_dir}")


if __name__ == "__main__":
    main()
