import re
from dataclasses import dataclass

from dani_api.rag.loader import KnowledgeDocument, load_markdown_documents

DEFAULT_CHUNK_SIZE = 1_200
DEFAULT_CHUNK_OVERLAP = 200

HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


@dataclass(frozen=True)
class KnowledgeChunk:
    """A searchable chunk created from a knowledge document."""

    content: str
    source: str
    title: str
    section: str | None
    chunk_index: int


@dataclass(frozen=True)
class MarkdownSection:
    """A section extracted from a Markdown document"""

    heading: str | None
    content: str


def split_markdown_sections(content: str) -> list[MarkdownSection]:
    """
    Split Markdown content at headings.

    Heading-only sections are not emitted as separate sections. Instead,
    their heading as carried forward as context for the next section.
    """
    sections: list[MarkdownSection] = []
    heading_stack: dict[int, str] = {}
    current_heading: str | None = None
    current_lines: list[str] = []

    def save_current_section() -> None:
        nonlocal current_lines

        section_content = "\n".join(current_lines).strip()

        # A useful section must contain more than only a Markdown heading.
        content_without_headings = "\n".join(
            line for line in current_lines if not HEADING_PATTERN.match(line.strip())
        ).strip()

        if section_content and content_without_headings:
            sections.append(
                MarkdownSection(heading=current_heading, content=section_content)
            )
        current_lines = []

    for line in content.splitlines():
        heading_match = HEADING_PATTERN.match(line.strip())

        if not heading_match:
            current_lines.append(line)
            continue

        save_current_section()

        level = len(heading_match.group(1))
        heading_text = heading_match.group(2).strip()

        heading_stack[level] = heading_text

        # Remove heading that belong to deeper, previous branches.
        heading_stack = {
            heading_level: heading_text
            for heading_level, heading_text in heading_stack.items()
            if heading_level <= level
        }

        current_heading = " > ".join(
            heading for _, heading in sorted(heading_stack.items())
        )

        current_lines = [line]

    save_current_section()

    return sections


def split_text_with_overlap(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """
    Split text into word-safe chunks with approximate character overlap.

    Args:
        text:
            Text to split.
        chunk_size:
            Maximum approximate number of characters in each chunk.
        chunk_overlap:
            Approximate number of characters repeated between chunks.
    Returns:
        Non-empty text chunks.

    Raises:
        ValueError:
            If the chunk settings are invalid.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk overlap must be smaller thank chunk_size.")

    words = text.split()

    if not words:
        return []

    chunks: list[str] = []
    start_index = 0

    while start_index < len(words):
        end_index = start_index
        current_length = 0

        while end_index < len(words):
            word = words[end_index]
            added_length = len(word) if end_index == start_index else len(word) + 1

            if current_length + added_length > chunk_size:
                break

            current_length += added_length
            end_index += 1

        # Handle a single unusually long word.
        if end_index == start_index:
            end_index = start_index + 1

        chunk = " ".join(words[start_index:end_index]).strip()

        if chunk:
            chunks.append(chunk)

        if end_index >= len(words):
            break

        next_start_index = end_index
        overlap_length = 0

        while next_start_index > start_index:
            previous_word = words[next_start_index - 1]
            added_length = len(previous_word)

            if overlap_length:
                added_length += 1

            if overlap_length + added_length > chunk_overlap:
                break

            overlap_length += added_length
            next_start_index -= 1

        # Ensure that the loop always moved forward.
        start_index = max(next_start_index, start_index + 1)

    return chunks


def chunk_document(
    document: KnowledgeDocument,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[KnowledgeChunk]:
    """Split one loaded knowledge document into searchable chunks."""
    chunks: list[KnowledgeChunk] = []
    chunk_index = 0

    sections = split_markdown_sections(document.content)

    for section in sections:
        section_chunks = split_text_with_overlap(
            text=section.content, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        for content in section_chunks:
            chunks.append(
                KnowledgeChunk(
                    content=content,
                    source=document.source,
                    title=document.title,
                    section=section.heading,
                    chunk_index=chunk_index,
                )
            )
            chunk_index += 1
    return chunks


def chunk_documents(
    documents: list[KnowledgeDocument],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[KnowledgeChunk]:
    """Split several knowledge documents into searchable chunks."""
    chunks: list[KnowledgeChunk] = []

    for document in documents:
        chunks.extend(
            chunk_document(
                document=document, chunk_size=chunk_size, chunk_overlap=chunk_overlap
            )
        )

    return chunks


if __name__ == "__main__":
    loaded_documents = load_markdown_documents()
    generated_chunks = chunk_documents(loaded_documents)

    print(
        f"Created {len(generated_chunks)} chunks "
        f"from {len(loaded_documents)} documents."
    )

    for chunk in generated_chunks:
        section = chunk.section or "No section"

        print(
            f"- {chunk.source} "
            f"[{chunk.chunk_index}] "
            f"{section}: "
            f"{len(chunk.content)} characters"
        )
