import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from time import perf_counter

import structlog
from dani_api.access import AccessTier
from dani_api.config import settings
from dani_api.conversation import ConversationMessage
from dani_api.llm import LanguageModel
from dani_api.mlflow_tracking import log_rag_metrics, start_rag_run
from dani_api.prompts import NO_ANSWER_PREFIX
from dani_api.rag.retrieval import (
    DEFAULT_RESULT_LIMIT,
    KnowledgeRetriever,
    RetrievalResult,
)

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class RagAnswer:
    """An answer generated from retrieved knowledge."""

    answer: str
    sources: list[RetrievalResult]


def build_context(
    results: list[RetrievalResult],
) -> str:
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


def build_retrieval_query(
    question: str,
    history: Sequence[ConversationMessage],
) -> str:
    """Build a retrieval query with recent conversational context."""

    if not history:
        return question

    recent_history = history[-4:]

    parts = [f"{message.role}: {message.content}" for message in recent_history]

    parts.append(f"user: {question}")

    return "\n".join(parts)


class RagService:
    """Answers questions using retrieved knowledge."""

    def __init__(
        self,
        retriever: KnowledgeRetriever | None = None,
        language_model: LanguageModel | None = None,
    ) -> None:
        self.retriever = retriever or KnowledgeRetriever()
        self.language_model = language_model

    def answer(
        self,
        question: str,
        tier: AccessTier = AccessTier.FREE,
        limit: int = DEFAULT_RESULT_LIMIT,
        score_threshold: float | None = None,
        history: Sequence[ConversationMessage] = (),
    ) -> RagAnswer:
        """Retrieve relevant context and generate a grounded answer."""

        normalized_question = question.strip()

        if not normalized_question:
            raise ValueError("Question cannot be empty.")

        effective_score_threshold = (
            settings.retrieval_score_threshold
            if score_threshold is None
            else score_threshold
        )

        retrieval_query = build_retrieval_query(
            normalized_question,
            history,
        )

        request_started_at = perf_counter()

        logger.info(
            "rag_request_started",
            question_length=len(normalized_question),
            history_count=len(history),
            access_tier=tier.value,
            result_limit=limit,
            score_threshold=effective_score_threshold,
        )

        retrieval_started_at = perf_counter()

        sources = self.retriever.retrieve(
            query=retrieval_query,
            limit=limit,
            score_threshold=effective_score_threshold,
        )

        retrieval_duration_ms = round(
            (perf_counter() - retrieval_started_at) * 1000,
            2,
        )

        if not sources:
            total_duration_ms = round(
                (perf_counter() - request_started_at) * 1000,
                2,
            )

            logger.warning(
                "retrieval_empty",
                access_tier=tier.value,
                result_count=0,
                history_count=len(history),
                retrieval_duration_ms=retrieval_duration_ms,
                duration_ms=total_duration_ms,
                score_threshold=effective_score_threshold,
            )

            return RagAnswer(
                answer=(
                    "I could not find enough relevant information "
                    "in Daniela's knowledge base to answer that question."
                ),
                sources=[],
            )

        context = build_context(sources)

        retrieved_source_count = len(sources)
        top_score = max(source.score for source in sources)

        language_model = self.language_model or LanguageModel(tier=tier)

        with start_rag_run(
            access_tier=tier.value,
            provider=language_model.provider,
            model=language_model.model,
            retrieval_limit=limit,
            score_threshold=effective_score_threshold,
        ):
            llm_started_at = perf_counter()

            generated_answer = language_model.generate_answer(
                question=normalized_question,
                context=context,
                history=history,
            )

            llm_duration_ms = round(
                (perf_counter() - llm_started_at) * 1000,
                2,
            )

            if generated_answer.startswith(NO_ANSWER_PREFIX):
                unsupported_answer = generated_answer.removeprefix(
                    NO_ANSWER_PREFIX
                ).strip()

                if not unsupported_answer:
                    unsupported_answer = (
                        "I could not find enough relevant information "
                        "in Daniela's knowledge base to answer that "
                        "question."
                    )

                generated_answer = unsupported_answer
                sources = []

            total_duration_ms = round(
                (perf_counter() - request_started_at) * 1000,
                2,
            )

            log_rag_metrics(
                question_length=len(normalized_question),
                source_count=retrieved_source_count,
                top_score=top_score,
                retrieval_duration_ms=retrieval_duration_ms,
                llm_duration_ms=llm_duration_ms,
                total_duration_ms=total_duration_ms,
                answer_length=len(generated_answer),
            )

        logger.info(
            "rag_request_completed",
            access_tier=tier.value,
            provider=language_model.provider,
            model=language_model.model,
            source_count=retrieved_source_count,
            returned_source_count=len(sources),
            history_count=len(history),
            top_score=top_score,
            retrieval_duration_ms=retrieval_duration_ms,
            llm_duration_ms=llm_duration_ms,
            duration_ms=total_duration_ms,
            answer_length=len(generated_answer),
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
        help=(
            "Optional minimum retrieval score. "
            "Uses the configured default when omitted."
        ),
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
        for index, source in enumerate(
            result.sources,
            start=1,
        ):
            print(
                f"{index}. {source.title} — "
                f"{source.section or 'Unknown section'} "
                f"[score={source.score:.4f}]"
            )
            print(f"   {source.source}")
