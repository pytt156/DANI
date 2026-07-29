from unittest.mock import Mock

from dani_api.api.dependencies import get_rag_service
from dani_api.main import app
from dani_api.rag.retrieval import RetrievalResult
from dani_api.rag.service import RagAnswer
from fastapi.testclient import TestClient


def test_chat_returns() -> None:
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
        answer="Generated answer.", sources=[source]
    )

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        client = TestClient(app)

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
        }

        rag_service.answer.assert_called_once_with(
            "What technologies does the example project use?"
        )
    finally:
        app.dependency_overrides.clear()


def test_chat_rejects_missing_message() -> None:
    rag_service = Mock()

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        client = TestClient(app)

        response = client.post(
            "/api/chat",
            json={},
        )
        assert response.status_code == 422
        rag_service.answer.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_chat_rejects_empty_message() -> None:
    rag_service = Mock()

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        client = TestClient(app)

        response = client.post(
            "/api/chat",
            json={"message": ""},
        )

        assert response.status_code == 422
        rag_service.answer.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_chat_rejects_message_that_is_too_long() -> None:
    rag_service = Mock()

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        client = TestClient(app)

        response = client.post(
            "/api/chat",
            json={"message": "x" * 2001},
        )

        assert response.status_code == 422
        rag_service.answer.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_chat_returns_400_for_value_error() -> None:
    rag_service = Mock()
    rag_service.answer.side_effect = ValueError("Question cannot be empty.")

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        client = TestClient(app)

        response = client.post(
            "/api/chat",
            json={"message": "   "},
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Question cannot be empty."}
    finally:
        app.dependency_overrides.clear()


def test_chat_returns_503_for_unexpected_error() -> None:
    rag_service = Mock()
    rag_service.answer.side_effect = RuntimeError("Service unavailable.")

    app.dependency_overrides[get_rag_service] = lambda: rag_service

    try:
        client = TestClient(app)

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


def test_health_check() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
