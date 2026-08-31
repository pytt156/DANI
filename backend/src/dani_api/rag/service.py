import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from time import perf_counter

import mlflow
import structlog
from mlflow.entities import SpanType

from dani_api.access import AccessTier
from dani_api.config import settings
from dani_api.conversation import ConversationMessage
from dani_api.llm import LanguageModel
from dani_api.mlflow_tracking import (
    log_rag_metrics,
    start_rag_run,
    start_rag_trace,
)
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


def build_context(results: list[RetrievalResult]) -> str:
    """Build model context from retrieved knowledge chunks."""
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
    """Build a retrieval query with conversation history when available."""
    if not history:
        return question

    lines = [f"{message.role}: {message.content}" for message in history]
    lines.append(f"user: {question}")

    return "\n".join(lines)


def select_response_sources(
    results: list[RetrievalResult],
) -> list[RetrievalResult]:
    """Return one user-facing source per knowledge document."""
    selected: list[RetrievalResult] = []
    seen_sources: set[str] = set()

    for result in results:
        if result.source in seen_sources:
            continue

        seen_sources.add(result.source)
        selected.append(result)

    return selected


def serialize_source(
    result: RetrievalResult,
    *,
    include_content: bool,
) -> dict[str, object]:
    """Serialize a retrieval result for MLflow tracing."""
    serialized: dict[str, object] = {
        "title": result.title,
        "source": result.source,
        "section": result.section,
        "chunk_index": result.chunk_index,
        "score": result.score,
    }

    if include_content:
        serialized["content"] = result.content

    return serialized


class RagService:
    """Answers questions using retrieved knowledge."""

    def __init__(
        self,
        retriever: KnowledgeRetriever | None = None,
        language_model: LanguageModel | None = None,
    ) -> None:
        self.retriever = retriever or KnowledgeRetriever()
        self.language_model = language_model

    def _provider_and_model(
        self,
        tier: AccessTier,
    ) -> tuple[str, str]:
        """Resolve provider and model without creating a new API client."""
        if self.language_model is not None:
            return (
                str(self.language_model.provider),
                str(self.language_model.model),
            )

        if tier is AccessTier.PREMIUM:
            return "openai", settings.openai_chat_model

        return "openrouter", settings.openrouter_chat_model

    def answer(
        self,
        question: str,
        tier: AccessTier = AccessTier.FREE,
        limit: int = DEFAULT_RESULT_LIMIT,
        score_threshold: float | None = None,
        history: Sequence[ConversationMessage] | None = None,
    ) -> RagAnswer:
        """Retrieve relevant context and generate a grounded answer."""
        normalized_question = question.strip()

        if not normalized_question:
            raise ValueError("Question cannot be empty.")

        normalized_history: Sequence[ConversationMessage]

        if history:
            normalized_history = list(history)
        else:
            normalized_history = ()

        effective_score_threshold = (
            settings.retrieval_score_threshold
            if score_threshold is None
            else score_threshold
        )

        retrieval_query = build_retrieval_query(
            normalized_question,
            normalized_history,
        )

        provider, model = self._provider_and_model(tier)

        request_started_at = perf_counter()

        logger.info(
            "rag_request_started",
            question_length=len(normalized_question),
            history_count=len(normalized_history),
            access_tier=tier.value,
            result_limit=limit,
            score_threshold=effective_score_threshold,
        )

        with (
            start_rag_trace(
                question=normalized_question,
                access_tier=tier.value,
                provider=provider,
                model=model,
                retrieval_limit=limit,
                score_threshold=effective_score_threshold,
            ) as trace_span,
            start_rag_run(
                access_tier=tier.value,
                provider=provider,
                model=model,
                retrieval_limit=limit,
                score_threshold=effective_score_threshold,
            ),
        ):
            retrieval_started_at = perf_counter()

            if trace_span is not None:
                with mlflow.start_span(
                    name="retrieve_context",
                    span_type=SpanType.RETRIEVER,
                ) as retrieval_span:
                    retrieval_span.set_inputs(
                        {
                            "query": retrieval_query,
                            "limit": limit,
                            "score_threshold": effective_score_threshold,
                        }
                    )

                    sources = self.retriever.retrieve(
                        query=retrieval_query,
                        limit=limit,
                        score_threshold=effective_score_threshold,
                    )

                    retrieval_span.set_outputs(
                        [
                            serialize_source(
                                source,
                                include_content=True,
                            )
                            for source in sources
                        ]
                    )

            else:
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
                generated_answer = (
                    "I could not find enough relevant information "
                    "in Daniela's knowledge base to answer that question."
                )

                total_duration_ms = round(
                    (perf_counter() - request_started_at) * 1000,
                    2,
                )

                log_rag_metrics(
                    question_length=len(normalized_question),
                    source_count=0,
                    top_score=None,
                    retrieval_duration_ms=retrieval_duration_ms,
                    llm_duration_ms=0.0,
                    total_duration_ms=total_duration_ms,
                    answer_length=len(generated_answer),
                )

                if trace_span is not None:
                    trace_span.set_outputs(
                        {
                            "answer": generated_answer,
                            "sources": [],
                        }
                    )

                logger.warning(
                    "retrieval_empty",
                    access_tier=tier.value,
                    history_count=len(normalized_history),
                    result_count=0,
                    retrieval_duration_ms=retrieval_duration_ms,
                    duration_ms=total_duration_ms,
                )

                return RagAnswer(
                    answer=generated_answer,
                    sources=[],
                )

            context = build_context(sources)

            language_model = self.language_model or LanguageModel(tier=tier)

            llm_started_at = perf_counter()

            if trace_span is not None:
                with mlflow.start_span(
                    name="generate_answer",
                    span_type=SpanType.TASK,
                ) as generation_span:
                    generation_span.set_inputs(
                        {
                            "question": normalized_question,
                            "history_count": len(normalized_history),
                            "source_count": len(sources),
                        }
                    )

                    generated_answer = language_model.generate_answer(
                        question=normalized_question,
                        context=context,
                        history=normalized_history,
                    )

                    generation_span.set_outputs(
                        {
                            "answer": generated_answer,
                        }
                    )

            else:
                generated_answer = language_model.generate_answer(
                    question=normalized_question,
                    context=context,
                    history=normalized_history,
                )

            llm_duration_ms = round(
                (perf_counter() - llm_started_at) * 1000,
                2,
            )

            total_duration_ms = round(
                (perf_counter() - request_started_at) * 1000,
                2,
            )

            top_score = max(source.score for source in sources)

            response_sources = select_response_sources(sources)

            log_rag_metrics(
                question_length=len(normalized_question),
                source_count=len(sources),
                top_score=top_score,
                retrieval_duration_ms=retrieval_duration_ms,
                llm_duration_ms=llm_duration_ms,
                total_duration_ms=total_duration_ms,
                answer_length=len(generated_answer),
            )

            if trace_span is not None:
                trace_span.set_outputs(
                    {
                        "answer": generated_answer,
                        "sources": [
                            serialize_source(
                                source,
                                include_content=False,
                            )
                            for source in response_sources
                        ],
                    }
                )

        logger.info(
            "rag_request_completed",
            access_tier=tier.value,
            provider=provider,
            model=model,
            source_count=len(sources),
            returned_source_count=len(response_sources),
            history_count=len(normalized_history),
            top_score=top_score,
            retrieval_duration_ms=retrieval_duration_ms,
            llm_duration_ms=llm_duration_ms,
            duration_ms=total_duration_ms,
            answer_length=len(generated_answer),
        )

        return RagAnswer(
            answer=generated_answer,
            sources=response_sources,
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
