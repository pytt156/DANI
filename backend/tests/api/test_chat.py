from collections.abc import Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from dani_api.access import (
    AccessContext,
    AccessTier,
    hash_access_key,
)
from dani_api.api.dependencies import get_rag_service
from dani_api.config import settings
from dani_api.conversation import ConversationMessage
from dani_api.main import app
from dani_api.rag.retrieval import RetrievalResult
from dani_api.rag.service import RagAnswer


@pytest.fixture
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def test_chat_returns(client: TestClient) -> None:
    rag_service = Mock()

    source = RetrievalResult(
        content="Example project uses FastApi.",
        source="example.md",
        title="Example project",
        section="Technology",
        chunk_index=0,
        score=0.91,
    )

    rag_service.answer.return_value = RagAnswer(
        answer="Generated answer.",
        sources=[source],
    )

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        response = client.post(
            "/api/chat",
            json={"message": "What technologies does the example project use?"},
        )

        assert response.status_code == 200

        assert response.json() == {
            "answer": "Generated answer.",
            "sources": [
                {
                    "title": "Example project",
                    "source": "example.md",
                    "section": "Technology",
                    "chunk_index": 0,
                    "score": 0.91,
                }
            ],
            "access_tier": "free",
        }

        rag_service.answer.assert_called_once_with(
            "What technologies does the example project use?",
            access=AccessContext(
                tier=AccessTier.FREE,
                key_id=None,
            ),
            history=[],
        )

    finally:
        app.dependency_overrides.clear()


def test_chat_passes_history_to_rag_service(
    client: TestClient,
) -> None:
    rag_service = Mock()

    rag_service.answer.return_value = RagAnswer(
        answer="DANI used Docker.",
        sources=[],
    )

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        response = client.post(
            "/api/chat",
            json={
                "message": "Which of those used Docker?",
                "history": [
                    {
                        "role": "user",
                        "content": "What has Daniela built?",
                    },
                    {
                        "role": "assistant",
                        "content": "Daniela has built DANI and other MLOps projects.",
                    },
                ],
            },
        )

        assert response.status_code == 200

        rag_service.answer.assert_called_once_with(
            "Which of those used Docker?",
            access=AccessContext(
                tier=AccessTier.FREE,
                key_id=None,
            ),
            history=[
                ConversationMessage(
                    role="user",
                    content="What has Daniela built?",
                ),
                ConversationMessage(
                    role="assistant",
                    content="Daniela has built DANI and other MLOps projects.",
                ),
            ],
        )

    finally:
        app.dependency_overrides.clear()


def test_chat_passes_premium_access_context(
    client: TestClient,
    monkeypatch,
) -> None:
    premium_key = "dani_test_premium_key"

    monkeypatch.setattr(
        settings,
        "premium_access_key_hashes",
        {
            "application-1": hash_access_key(premium_key),
        },
    )

    rag_service = Mock()

    rag_service.answer.return_value = RagAnswer(
        answer="Generated answer.",
        sources=[],
    )

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        response = client.post(
            "/api/chat",
            json={"message": "Example question"},
            headers={
                "X-DANI-Access-Key": premium_key,
            },
        )

        assert response.status_code == 200
        assert response.json()["access_tier"] == "premium"

        rag_service.answer.assert_called_once_with(
            "Example question",
            access=AccessContext(
                tier=AccessTier.PREMIUM,
                key_id="application-1",
            ),
            history=[],
        )

    finally:
        app.dependency_overrides.clear()


def test_chat_rejects_missing_message(
    client: TestClient,
) -> None:
    rag_service = Mock()

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        response = client.post(
            "/api/chat",
            json={},
        )

        assert response.status_code == 422
        rag_service.answer.assert_not_called()

    finally:
        app.dependency_overrides.clear()


def test_chat_rejects_empty_message(
    client: TestClient,
) -> None:
    rag_service = Mock()

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        response = client.post(
            "/api/chat",
            json={"message": ""},
        )

        assert response.status_code == 422
        rag_service.answer.assert_not_called()

    finally:
        app.dependency_overrides.clear()


def test_chat_rejects_whitespace_only_message(
    client: TestClient,
) -> None:
    rag_service = Mock()

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        response = client.post(
            "/api/chat",
            json={"message": "   "},
        )

        assert response.status_code == 422
        rag_service.answer.assert_not_called()

    finally:
        app.dependency_overrides.clear()


def test_chat_rejects_message_that_is_too_long(
    client: TestClient,
) -> None:
    rag_service = Mock()

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        response = client.post(
            "/api/chat",
            json={"message": "x" * 2001},
        )

        assert response.status_code == 422
        rag_service.answer.assert_not_called()

    finally:
        app.dependency_overrides.clear()


def test_chat_rejects_too_much_history(
    client: TestClient,
) -> None:
    rag_service = Mock()

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    history = [
        {
            "role": "user",
            "content": f"Message {index}",
        }
        for index in range(9)
    ]

    try:
        response = client.post(
            "/api/chat",
            json={
                "message": "Example question",
                "history": history,
            },
        )

        assert response.status_code == 422
        rag_service.answer.assert_not_called()

    finally:
        app.dependency_overrides.clear()


def test_chat_rejects_invalid_history_role(
    client: TestClient,
) -> None:
    rag_service = Mock()

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        response = client.post(
            "/api/chat",
            json={
                "message": "Example question",
                "history": [
                    {
                        "role": "system",
                        "content": "Example history",
                    }
                ],
            },
        )

        assert response.status_code == 422
        rag_service.answer.assert_not_called()

    finally:
        app.dependency_overrides.clear()


def test_chat_returns_503_for_service_value_error(
    client: TestClient,
) -> None:
    rag_service = Mock()

    rag_service.answer.side_effect = ValueError("OPENROUTER_API_KEY is not configured.")

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        response = client.post(
            "/api/chat",
            json={"message": "Example question"},
        )

        assert response.status_code == 503

        assert response.json() == {
            "detail": "The knowledge service is temporarily unavailable"
        }

    finally:
        app.dependency_overrides.clear()


def test_chat_returns_503_for_unexpected_error(
    client: TestClient,
) -> None:
    rag_service = Mock()

    rag_service.answer.side_effect = RuntimeError("Service unavailable.")

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        response = client.post(
            "/api/chat",
            json={"message": "Example question"},
        )

        assert response.status_code == 503

        assert response.json() == {
            "detail": "The knowledge service is temporarily unavailable"
        }

    finally:
        app.dependency_overrides.clear()


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_response_contains_request_id(
    client: TestClient,
) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["x-request-id"]


def test_existing_request_id_is_reused(
    client: TestClient,
) -> None:
    request_id = "test-request-123"

    response = client.get(
        "/health",
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == request_id
