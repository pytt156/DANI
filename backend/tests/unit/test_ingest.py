from dani_api.rag.chunker import KnowledgeChunk
from dani_api.rag.ingest import create_payload, create_point_id


def make_chunk(
    *,
    content: str = "Daniela uses FastAPI.",
    source: str = "projects/example.md",
    title: str = "Example Project",
    section: str | None = "Example Project > Stack",
    chunk_index: int = 0,
) -> KnowledgeChunk:
    return KnowledgeChunk(
        content=content,
        source=source,
        title=title,
        section=section,
        chunk_index=chunk_index,
    )


def test_create_point_id_is_deterministic() -> None:
    chunk = make_chunk()

    assert create_point_id(chunk) == create_point_id(chunk)


def test_create_point_id_changes_when_content_changes() -> None:
    original = make_chunk(content="Daniela uses FastAPI.")
    changed = make_chunk(content="Daniela uses FastAPI and Qdrant.")

    assert create_point_id(original) != create_point_id(changed)


def test_create_point_id_changes_when_source_changes() -> None:
    original = make_chunk(source="projects/example.md")
    changed = make_chunk(source="projects/another.md")

    assert create_point_id(original) != create_point_id(changed)


def test_create_payload_contains_chunk_metadata() -> None:
    chunk = make_chunk()

    assert create_payload(chunk) == {
        "content": "Daniela uses FastAPI.",
        "source": "projects/example.md",
        "title": "Example Project",
        "section": "Example Project > Stack",
        "chunk_index": 0,
    }
