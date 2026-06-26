import re


def split_markdown(text: str, max_chars: int, overlap: int) -> list:
    sections = re.split(r'(?=^#{1,6}\s)', text, flags=re.MULTILINE)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if len(section) <= max_chars:
            chunks.append(section)
        else:
            chunks.extend(_split_by_chars(section, max_chars, overlap))
    return _merge_small_chunks(chunks)


def _split_by_chars(text: str, max_chars: int, overlap: int) -> list:
    parts = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            newline = text.rfind('\n', start + max_chars // 2, end)
            if newline != -1:
                end = newline + 1
        parts.append(text[start:end])
        start = end - overlap if end < len(text) else len(text)
    return parts


def _merge_small_chunks(chunks: list, min_chars: int = 300) -> list:
    merged = []
    buf = ''
    for chunk in chunks:
        if not buf:
            buf = chunk
        elif len(buf) + len(chunk) <= min_chars:
            buf += '\n\n' + chunk
        else:
            merged.append(buf)
            buf = chunk
    if buf:
        merged.append(buf)
    return merged


def generate_manifest(chunks: list, sources: list, chunk_size: int = 0, overlap: int = 0) -> dict:
    return {
        "total_chunks": len(chunks),
        "sources": list(set(sources)),
        "chunk_size": chunk_size,
        "overlap": overlap,
    }
