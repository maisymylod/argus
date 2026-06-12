"""Split knowledge-base markdown into retrievable chunks, one per section."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

KB_DIR = Path(__file__).resolve().parents[2] / "data" / "kb"


@dataclass(frozen=True)
class Chunk:
    source: str  # file name, e.g. sentinel-2.md
    heading: str  # section heading
    text: str  # section body


def chunk_markdown(markdown: str, source: str) -> list[Chunk]:
    """Split on level-2 (##) headings; the level-1 title seeds the first heading."""
    chunks: list[Chunk] = []
    heading = source
    body: list[str] = []

    def flush() -> None:
        text = "\n".join(body).strip()
        if text:
            chunks.append(Chunk(source=source, heading=heading, text=text))

    for line in markdown.splitlines():
        if line.startswith("## "):
            flush()
            heading = line[3:].strip()
            body = []
        elif line.startswith("# "):
            heading = line[2:].strip()
        else:
            body.append(line)
    flush()
    return chunks


def load_kb_chunks(kb_dir: Path = KB_DIR) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(kb_dir.glob("*.md")):
        chunks.extend(chunk_markdown(path.read_text(), path.name))
    return chunks
