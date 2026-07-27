import argparse
from dataclasses import dataclass

from dani_api.llm import LanguageModel
from dani_api.rag.retrieval import (
    DEFAULT_RESULT_LIMIT,
    KnowledgeRetriever,
    RetrievalResult,
)


@dataclass(frozen=True)
class RagAnswer:
    """An answer generated from retrieved knowledge."""

    answer: str
    sources: list[RetrievalResult]


def build_context(results: list[RetrievalResult]) -> str:
    """Build model context from retrieved chunks."""
    sections: list[str] = []

    for index, result in enumerate(results, start=1):
        sections.append(
            "\n".join(
                [
                    f"[Source {index}]",
                    f"Title: {result.title}",
                    f"File: {result.source}",
                    f"Section: {result.section or 'Unknown'}",
                    result.content,
                ]
            )
        )

    return "\n\n".join(sections)


class RagService:
    """Answers questions using retrieved knowledge."""

    def __init__(
        self,
        retriever: KnowledgeRetriever | None = None,
        language_model: LanguageModel | None = None,
    ) -> None:
        self.retriever = retriever or KnowledgeRetriever()
        self.language_model = language_model or LanguageModel()

    def answer(
        self,
        question: str,
        limit: int = DEFAULT_RESULT_LIMIT,
        score_threshold: float | None = None,
    ) -> RagAnswer:
        """Retrieve relevant context and generate a grounded answer."""
        normalized_question = question.strip()

        if not normalized_question:
            raise ValueError("Question cannot be empty.")

        sources = self.retriever.retrieve(
            query=normalized_question,
            limit=limit,
            score_threshold=score_threshold,
        )

        if not sources:
            return RagAnswer(
                answer=(
                    "I could not find enough relevant information "
                    "in Daniela's knowledge base to answer that question."
                ),
                sources=[],
            )

        context = build_context(sources)

        generated_answer = self.language_model.generate_answer(
            question=normalized_question,
            context=context,
        )

        return RagAnswer(
            answer=generated_answer,
            sources=sources,
        )


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Ask a question using the DANI knowledge base."
    )
    parser.add_argument(
        "question",
        help="Question to answer.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_RESULT_LIMIT,
        help="Maximum number of retrieved knowledge chunks.",
    )
    parser.add_argument(
        "--score-threshold",
        type=float,
        default=None,
        help="Optional minimum retrieval score.",
    )

    return parser


if __name__ == "__main__":
    arguments = build_argument_parser().parse_args()
    rag_service = RagService()

    try:
        result = rag_service.answer(
            question=arguments.question,
            limit=arguments.limit,
            score_threshold=arguments.score_threshold,
        )
    except Exception as error:
        raise SystemExit(f"RAG answer generation failed: {error}") from error

    print("\nAnswer:\n")
    print(result.answer)

    print("\nSources:\n")

    if not result.sources:
        print("No sources.")
    else:
        for index, source in enumerate(result.sources, start=1):
            print(
                f"{index}. {source.title} — "
                f"{source.section or 'Unknown section'} "
                f"[score={source.score:.4f}]"
            )
            print(f"   {source.source}")
