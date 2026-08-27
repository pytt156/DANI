from unittest.mock import Mock, patch

import pytest

from dani_api.access import AccessTier
from dani_api.rag.retrieval import RetrievalResult
from dani_api.rag.service import RagService


def test_answer_rejects_empty_question() -> None:
    retriever = Mock()
    language_model = Mock()

    service = RagService(
        retriever=retriever,
        language_model=language_model,
    )

    with pytest.raises(ValueError, match="Question cannot be empty."):
        service.answer("    ")

    retriever.retrieve.assert_not_called()
    language_model.generate_answer.assert_not_called()


def test_answer_returns_generated_answer_and_sources() -> None:
    source = RetrievalResult(
        content="Example project uses FastAPI.",
        source="example.md",
        title="Example project",
        section="Technology",
        chunk_index=0,
        score=0.91,
    )

    retriever = Mock()
    retriever.retrieve.return_value = [source]

    language_model = Mock()
    language_model.generate_answer.return_value = "Generated answer."

    service = RagService(
        retriever=retriever,
        language_model=language_model,
    )

    result = service.answer(
        "What technologies does the example project use?",
        tier=AccessTier.PREMIUM,
    )

    assert result.answer == "Generated answer."
    assert result.sources == [source]

    retriever.retrieve.assert_called_once_with(
        query="What technologies does the example project use?",
        limit=5,
        score_threshold=None,
    )

    language_model.generate_answer.assert_called_once_with(
        question="What technologies does the example project use?",
        context=(
            "[Source 1]\n"
            "Title: Example project\n"
            "File: example.md\n"
            "Section: Technology\n"
            "Example project uses FastAPI."
        ),
    )


def test_answer_returns_fallback() -> None:
    retriever = Mock()
    retriever.retrieve.return_value = []

    language_model = Mock()

    service = RagService(
        retriever=retriever,
        language_model=language_model,
    )

    result = service.answer("What is Daniela's favourite planet?")

    assert result.answer == (
        "I could not find enough relevant information "
        "in Daniela's knowledge base to answer that question."
    )

    assert result.sources == []

    language_model.generate_answer.assert_not_called()


def test_answer_passes_custom_retrieval_settings() -> None:
    source = RetrievalResult(
        content="Example content.",
        source="example.md",
        title="Example title",
        section="Example section",
        chunk_index=0,
        score=0.91,
    )

    retriever = Mock()
    retriever.retrieve.return_value = [source]

    language_model = Mock()
    language_model.generate_answer.return_value = "Generated answer."

    service = RagService(
        retriever=retriever,
        language_model=language_model,
    )

    service.answer(
        "Example question",
        limit=3,
        score_threshold=0.45,
    )

    retriever.retrieve.assert_called_once_with(
        query="Example question",
        limit=3,
        score_threshold=0.45,
    )


def test_answer_creates_free_language_model_by_default() -> None:
    source = RetrievalResult(
        content="Example content.",
        source="example.md",
        title="Example title",
        section="Example section",
        chunk_index=0,
        score=0.91,
    )

    retriever = Mock()
    retriever.retrieve.return_value = [source]

    language_model = Mock()
    language_model.generate_answer.return_value = "Generated answer."

    with patch(
        "dani_api.rag.service.LanguageModel",
        return_value=language_model,
    ) as language_model_class:
        service = RagService(retriever=retriever)

        service.answer("Example question")

    language_model_class.assert_called_once_with(
        tier=AccessTier.FREE,
    )


def test_answer_creates_premium_language_model_for_premium_tier() -> None:
    source = RetrievalResult(
        content="Example content.",
        source="example.md",
        title="Example title",
        section="Example section",
        chunk_index=0,
        score=0.91,
    )

    retriever = Mock()
    retriever.retrieve.return_value = [source]

    language_model = Mock()
    language_model.generate_answer.return_value = "Generated answer."

    with patch(
        "dani_api.rag.service.LanguageModel",
        return_value=language_model,
    ) as language_model_class:
        service = RagService(retriever=retriever)

        service.answer(
            "Example question",
            tier=AccessTier.PREMIUM,
        )

    language_model_class.assert_called_once_with(
        tier=AccessTier.PREMIUM,
    )
