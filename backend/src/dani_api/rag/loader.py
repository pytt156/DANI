from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"


@dataclass(frozen=True)
class KnowledgeDocument:
    """A source document loaded from the knowledge base."""

    content: str
    source: str
    title: str


def extract_title(content: str, fallback: str) -> str:
    """
    Extract the first markdown H1 heading.

    Falls back to the filename stem when no H1 heading exists.
    """

    for line in content.splitlines():
        stripped_line = line.strip()

        if stripped_line.startswith("# "):
            title = stripped_line.removeprefix("# ").strip()

            if title:
                return title

    return fallback


def load_markdown_documents(
    knowledge_dir: Path = DEFAULT_KNOWLEDGE_DIR,
) -> list[KnowledgeDocument]:
    """
    Load all non-empty Markdown files from the knowledge directory.

    Args:
        knowledge_dir:
            Directory containing the Markfown knowledge-base files.

    Returns:
        Loaded documents sorted by their source path.

    Raises:
        FileNotFoundError:
            If the knowledge directory does not exist.
        NotADirectoryError:
            If the supplied path is not a directory.
    """
    knowledge_dir = knowledge_dir.resolve()

    if not knowledge_dir.exists():
        raise FileNotFoundError(f"Knowledge directory does not exist: {knowledge_dir}")

    if not knowledge_dir.is_dir():
        raise NotADirectoryError(f"Knowledge directory does not exist: {knowledge_dir}")

    documents: list[KnowledgeDocument] = []

    for file_path in sorted(knowledge_dir.rglob("*.md")):
        content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            continue

        source = file_path.relative_to(knowledge_dir).as_posix()
        title = extract_title(
            content=content,
            fallback=file_path.stem.replace("-", " ").replace("_", " ").title(),
        )

        documents.append(KnowledgeDocument(content=content, source=source, title=title))

    return documents


if __name__ == "__main__":
    loaded_documents = load_markdown_documents()

    print(
        f"Loaded {len(loaded_documents)} Markdown documents "
        f"from {DEFAULT_KNOWLEDGE_DIR}."
    )

    for document in loaded_documents:
        print(f"- {document.source}: {document.title}")
