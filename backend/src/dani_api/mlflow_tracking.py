from collections.abc import Iterator
from contextlib import contextmanager

import mlflow
import structlog

from dani_api.config import settings

logger = structlog.get_logger(__name__)


def configure_mlflow() -> None:
    """Configure MLflow tracking for DANI."""
    if not settings.mlflow_enabled:
        return

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)


@contextmanager
def start_rag_run(
    *,
    access_tier: str,
    provider: str,
    model: str,
    retrieval_limit: int,
    score_threshold: float | None,
) -> Iterator[mlflow.ActiveRun | None]:
    """Start an optional MLflow run for one DANI RAG request."""

    if not settings.mlflow_enabled:
        yield None
        return

    run: mlflow.ActiveRun | None = None

    try:
        configure_mlflow()

        run = mlflow.start_run()

        mlflow.log_params(
            {
                "access_tier": access_tier,
                "provider": provider,
                "model": model,
                "embedding_model": settings.openai_embedding_model,
                "retrieval_limit": retrieval_limit,
                "score_threshold": (
                    score_threshold if score_threshold is not None else "none"
                ),
            }
        )

        mlflow.set_tags(
            {
                "request_type": "rag_chat",
                "environment": settings.environment,
            }
        )

    except Exception as error:  # noqa: BLE001
        logger.warning(
            "mlflow_run_start_failed",
            error_type=type(error).__name__,
        )

        if run is not None:
            try:
                mlflow.end_run(status="FAILED")
            except Exception:  # noqa: BLE001
                logger.warning("mlflow_run_cleanup_failed")

        yield None
        return

    try:
        yield run

    finally:
        try:
            mlflow.end_run()
        except Exception as error:  # noqa: BLE001
            logger.warning(
                "mlflow_run_end_failed",
                error_type=type(error).__name__,
            )


def log_rag_metrics(
    *,
    question_length: int,
    source_count: int,
    top_score: float | None,
    retrieval_duration_ms: float,
    llm_duration_ms: float,
    total_duration_ms: float,
    answer_length: int,
) -> None:
    """Log RAG request metrics when an MLflow run is available."""

    if not settings.mlflow_enabled:
        return

    if mlflow.active_run() is None:
        return

    metrics: dict[str, float] = {
        "question_length": float(question_length),
        "source_count": float(source_count),
        "retrieval_duration_ms": retrieval_duration_ms,
        "llm_duration_ms": llm_duration_ms,
        "total_duration_ms": total_duration_ms,
        "answer_length": float(answer_length),
    }

    if top_score is not None:
        metrics["top_score"] = top_score

    try:
        mlflow.log_metrics(metrics)

    except Exception as error:  # noqa: BLE001
        logger.warning(
            "mlflow_metrics_log_failed",
            error_type=type(error).__name__,
        )
