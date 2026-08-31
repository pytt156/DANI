from dani_api.access import (
    AccessContext,
    AccessTier,
    hash_access_key,
    resolve_access,
)
from dani_api.config import settings


def test_missing_access_key_is_free() -> None:
    assert resolve_access(None) == AccessContext(
        tier=AccessTier.FREE,
        key_id=None,
    )


def test_empty_access_key_is_free() -> None:
    assert resolve_access("   ") == AccessContext(
        tier=AccessTier.FREE,
        key_id=None,
    )


def test_invalid_access_key_is_free(monkeypatch) -> None:
    monkeypatch.setattr(
        settings,
        "premium_access_key_hashes",
        {
            "key-1": hash_access_key("correct-key"),
        },
    )

    assert resolve_access("wrong-key") == AccessContext(
        tier=AccessTier.FREE,
        key_id=None,
    )


def test_valid_access_key_is_premium(monkeypatch) -> None:
    premium_key = "dani_test_premium_key"

    monkeypatch.setattr(
        settings,
        "premium_access_key_hashes",
        {
            "key-1": hash_access_key(premium_key),
        },
    )

    assert resolve_access(premium_key) == AccessContext(
        tier=AccessTier.PREMIUM,
        key_id="key-1",
    )


def test_multiple_access_keys_are_supported(monkeypatch) -> None:
    first_key = "dani_first"
    second_key = "dani_second"

    monkeypatch.setattr(
        settings,
        "premium_access_key_hashes",
        {
            "key-1": hash_access_key(first_key),
            "key-2": hash_access_key(second_key),
        },
    )

    assert resolve_access(second_key) == AccessContext(
        tier=AccessTier.PREMIUM,
        key_id="key-2",
    )
