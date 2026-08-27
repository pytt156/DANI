from collections.abc import Generator
from unittest.mock import Mock

import pytest
from dani_api.api.dependencies import get_rag_service
from dani_api.main import app
from dani_api.rag.retrieval import RetrievalResult
from dani_api.rag.service import RagAnswer
from fastapi.testclient import TestClient


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
            "What technologies does the example project use?"
        )
    finally:
        app.dependency_overrides.clear()


def test_chat_rejects_missing_message(client: TestClient) -> None:
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


def test_chat_rejects_empty_message(client: TestClient) -> None:
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


def test_chat_rejects_message_that_is_too_long(client: TestClient) -> None:
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


def test_chat_returns_400_for_value_error(client: TestClient) -> None:
    rag_service = Mock()
    rag_service.answer.side_effect = ValueError("Question cannot be empty.")

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        response = client.post(
            "/api/chat",
            json={"message": "   "},
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Question cannot be empty."}
    finally:
        app.dependency_overrides.clear()


def test_chat_returns_503_for_unexpected_error(client: TestClient) -> None:
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


def test_response_contains_request_id(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["x-request-id"]


def test_existing_request_id_is_reused(client: TestClient) -> None:
    request_id = "test-request-123"

    response = client.get(
        "/health",
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == request_id
