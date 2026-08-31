from unittest.mock import MagicMock, patch

from dani_api.mlflow_tracking import (
    start_rag_run,
    start_rag_trace,
)


def test_rag_run_includes_key_id_tag() -> None:
    run = MagicMock()

    with (
        patch(
            "dani_api.mlflow_tracking.configure_mlflow",
            return_value=True,
        ),
        patch(
            "dani_api.mlflow_tracking.mlflow.start_run",
            return_value=run,
        ),
        patch(
            "dani_api.mlflow_tracking.mlflow.log_params",
        ),
        patch(
            "dani_api.mlflow_tracking.mlflow.set_tags",
        ) as set_tags,
        patch(
            "dani_api.mlflow_tracking.mlflow.end_run",
        ),start_rag_run(
        access_tier="premium",
        key_id="application-1",
        provider="openai",
        model="gpt-5-mini",
        retrieval_limit=5,
        score_threshold=0.3,
    )
    ):
        pass

    tags = set_tags.call_args.args[0]

    assert tags["key_id"] == "application-1"
    assert tags["request_type"] == "rag_chat"


def test_rag_run_omits_key_id_for_free_access() -> None:
    run = MagicMock()

    with (
        patch(
            "dani_api.mlflow_tracking.configure_mlflow",
            return_value=True,
        ),
        patch(
            "dani_api.mlflow_tracking.mlflow.start_run",
            return_value=run,
        ),
        patch(
            "dani_api.mlflow_tracking.mlflow.log_params",
        ),
        patch(
            "dani_api.mlflow_tracking.mlflow.set_tags",
        ) as set_tags,
        patch(
            "dani_api.mlflow_tracking.mlflow.end_run",
        ),start_rag_run(
        access_tier="free",
        key_id=None,
        provider="openrouter",
        model="openrouter/free",
        retrieval_limit=5,
        score_threshold=0.3,
    )
    ):
        pass

    tags = set_tags.call_args.args[0]

    assert "key_id" not in tags


def test_rag_trace_includes_key_id() -> None:
    span = MagicMock()

    span_context = MagicMock()
    span_context.__enter__.return_value = span

    with (
        patch(
            "dani_api.mlflow_tracking.configure_mlflow",
            return_value=True,
        ),
        patch(
            "dani_api.mlflow_tracking.mlflow.start_span",
            return_value=span_context,
        ),
        patch(
            "dani_api.mlflow_tracking.mlflow.update_current_trace",
        ) as update_trace,start_rag_trace(
        question="Example question",
        access_tier="premium",
        key_id="application-1",
        provider="openai",
        model="gpt-5-mini",
        retrieval_limit=5,
        score_threshold=0.3,
    )
    ):
        pass

    span.set_attribute.assert_any_call(
        "key_id",
        "application-1",
    )

    trace_tags = update_trace.call_args.kwargs["tags"]

    assert trace_tags["key_id"] == "application-1"
    assert trace_tags["access_tier"] == "premium"
    assert trace_tags["provider"] == "openai"


def test_rag_trace_omits_key_id_for_free_access() -> None:
    span = MagicMock()

    span_context = MagicMock()
    span_context.__enter__.return_value = span

    with (
        patch(
            "dani_api.mlflow_tracking.configure_mlflow",
            return_value=True,
        ),
        patch(
            "dani_api.mlflow_tracking.mlflow.start_span",
            return_value=span_context,
        ),
        patch(
            "dani_api.mlflow_tracking.mlflow.update_current_trace",
        ) as update_trace,start_rag_trace(
        question="Example question",
        access_tier="free",
        key_id=None,
        provider="openrouter",
        model="openrouter/free",
        retrieval_limit=5,
        score_threshold=0.3,
    )
    ):
        pass

    key_id_calls = [
        call
        for call in span.set_attribute.call_args_list
        if call.args and call.args[0] == "key_id"
    ]

    assert key_id_calls == []

    trace_tags = update_trace.call_args.kwargs["tags"]

    assert "key_id" not in trace_tags
