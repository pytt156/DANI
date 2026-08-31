import os
import socket
from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache
from urllib.parse import urlparse

import mlflow
import structlog
from mlflow import openai as mlflow_openai
from mlflow.entities import LiveSpan, SpanType
from structlog.contextvars import get_contextvars

from dani_api.config import settings

logger = structlog.get_logger(__name__)
_openai_autolog_enabled = False

MLFLOW_CONNECT_TIMEOUT_SECONDS = 0.5


def configure_mlflow_client() -> None:
    """Configure MLflow HTTP behavior for best-effort tracking."""

    os.environ["MLFLOW_HTTP_REQUEST_TIMEOUT"] = str(
        int(settings.mlflow_http_request_timeout)
    )
    os.environ["MLFLOW_HTTP_REQUEST_MAX_RETRIES"] = str(
        int(settings.mlflow_http_request_max_retries)
    )


@lru_cache(maxsize=1)
def mlflow_server_available() -> bool:
    """Return whether the configured MLflow server is reachable."""

    if not settings.mlflow_enabled:
        return False

    parsed_uri = urlparse(settings.mlflow_tracking_uri)

    if parsed_uri.scheme not in {"http", "https"}:
        return True

    if parsed_uri.hostname is None:
        logger.warning(
            "mlflow_tracking_uri_invalid",
            tracking_uri=settings.mlflow_tracking_uri,
        )
        return False

    port = parsed_uri.port

    if port is None:
        port = 443 if parsed_uri.scheme == "https" else 80

    try:
        with socket.create_connection(
            (parsed_uri.hostname, port),
            timeout=MLFLOW_CONNECT_TIMEOUT_SECONDS,
        ):
            return True

    except OSError:
        logger.warning(
            "mlflow_server_unavailable",
            host=parsed_uri.hostname,
            port=port,
        )
        return False


def configure_openai_autolog() -> None:
    """Enable automatic tracing for OpenAI-compatible model calls."""

    global _openai_autolog_enabled

    if _openai_autolog_enabled:
        return

    try:
        mlflow_openai.autolog(
            log_traces=True,
            silent=True,
        )
        _openai_autolog_enabled = True

    except Exception as error:  # noqa: BLE001
        logger.warning(
            "mlflow_openai_autolog_failed",
            error_type=type(error).__name__,
        )


def configure_mlflow() -> bool:
    """Configure MLflow when its tracking server is reachable."""

    if not mlflow_server_available():
        return False

    configure_mlflow_client()

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    try:
        mlflow.set_experiment(settings.mlflow_experiment_name)

    except Exception as error:  # noqa: BLE001
        logger.warning(
            "mlflow_configuration_failed",
            error_type=type(error).__name__,
        )
        return False

    configure_openai_autolog()

    return True


@contextmanager
def start_rag_run(
    *,
    access_tier: str,
    provider: str,
    model: str,
    retrieval_limit: int,
    score_threshold: float | None,
) -> Generator[mlflow.ActiveRun | None]:
    """Start an optional MLflow run for one DANI RAG request."""

    if not configure_mlflow():
        yield None
        return

    run: mlflow.ActiveRun | None = None

    try:
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


@contextmanager
def start_rag_trace(
    *,
    question: str,
    access_tier: str,
    provider: str,
    model: str,
    retrieval_limit: int,
    score_threshold: float | None,
) -> Generator[LiveSpan | None]:
    """Create one end-to-end MLflow trace for a DANI request."""

    if not configure_mlflow():
        yield None
        return

    context = get_contextvars()
    request_id = context.get("request_id")

    with mlflow.start_span(
        name="dani_chat",
        span_type=SpanType.CHAIN,
    ) as span:
        span.set_inputs(
            {
                "question": question,
            }
        )

        span.set_attribute("access_tier", access_tier)
        span.set_attribute("provider", provider)
        span.set_attribute("model", model)
        span.set_attribute(
            "embedding_model",
            settings.openai_embedding_model,
        )
        span.set_attribute(
            "retrieval_limit",
            retrieval_limit,
        )
        span.set_attribute(
            "score_threshold",
            score_threshold if score_threshold is not None else "none",
        )

        mlflow.update_current_trace(
            client_request_id=(str(request_id) if request_id is not None else None),
            request_preview=question,
            tags={
                "environment": settings.environment,
                "access_tier": access_tier,
                "provider": provider,
            },
        )

        yield span
