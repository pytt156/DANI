import pytest

from dani_api.rag.retrieval import (
    payload_integer,
    payload_optional_string,
    payload_string,
)


def test_payload_string_returns() -> None:
    payload = {"title": "Example title"}
    result = payload_string(payload, "title")

    assert result == "Example title"


def test_payload_string_rejects_non_string() -> None:
    payload = {"title": 123}

    with pytest.raises(
        TypeError, match="Qdrant payload field 'title' must be a string"
    ):
        payload_string(payload, "title")


def test_payload_optional_string() -> None:
    payload = {"section": "Architecture"}

    result = payload_optional_string(payload, "section")

    assert result == "Architecture"


def test_payload_optional_string_none() -> None:
    payload = {"section": None}

    result = payload_optional_string(payload, "section")

    assert result is None


def test_payload_integer_returns_integer_value() -> None:
    payload = {"chunk_index": 3}

    result = payload_integer(payload, "chunk_index")

    assert result == 3


def test_payload_integer_rejects_non_integer_value() -> None:
    payload = {"chunk_index": "3"}

    with pytest.raises(
        TypeError,
        match="Qdrant payload field 'chunk_index' must be an integer.",
    ):
        payload_integer(payload, "chunk_index")
