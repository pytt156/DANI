from dani_api.rag.retrieval import RetrievalResult
from dani_api.rag.service import build_context


def test_build_context_formats_single_result() -> None:
    result = RetrievalResult(
        content="Example content.",
        source="example.md",
        title="Example title",
        section="Example section",
        chunk_index=0,
        score=0.91,
    )

    context = build_context([result])

    assert context == (
        "[Source 1]\n"
        "Title: Example title\n"
        "File: example.md\n"
        "Section: Example section\n"
        "Example content."
    )


def test_build_context_uses_uknown() -> None:
    result = RetrievalResult(
        content="Example content.",
        source="example.md",
        title="Example title",
        section=None,
        chunk_index=0,
        score=0.91,
    )

    context = build_context([result])

    assert context == (
        "[Source 1]\n"
        "Title: Example title\n"
        "File: example.md\n"
        "Section: Unknown\n"
        "Example content."
    )


def test_build_context_formats_multiple_results() -> None:
    first_result = RetrievalResult(
        content="First content.",
        source="first.md",
        title="First title",
        section="First section",
        chunk_index=0,
        score=0.91,
    )

    second_result = RetrievalResult(
        content="Second content.",
        source="second.md",
        title="Second title",
        section="Second section",
        chunk_index=1,
        score=0.85,
    )

    context = build_context([first_result, second_result])

    expected_context = (
        "[Source 1]\n"
        "Title: First title\n"
        "File: first.md\n"
        "Section: First section\n"
        "First content.\n\n"
        "[Source 2]\n"
        "Title: Second title\n"
        "File: second.md\n"
        "Section: Second section\n"
        "Second content."
    )

    assert context == expected_context
