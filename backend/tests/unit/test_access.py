from dani_api.access import AccessTier, hash_access_key, resolve_access_tier
from dani_api.config import settings


def test_missing_access_key_is_free() -> None:
    assert resolve_access_tier(None) is AccessTier.FREE


def test_empty_access_key_is_free() -> None:
    assert resolve_access_tier("   ") is AccessTier.FREE


def test_invalid_access_key_is_free(monkeypatch) -> None:
    monkeypatch.setattr(
        settings,
        "premium_access_key_hashes",
        hash_access_key("correct-key"),
    )

    assert resolve_access_tier("wrong-key") is AccessTier.FREE


def test_valid_access_key_is_premium(monkeypatch) -> None:
    premium_key = "dani_test_premium_key"

    monkeypatch.setattr(
        settings,
        "premium_access_key_hashes",
        hash_access_key(premium_key),
    )

    assert resolve_access_tier(premium_key) is AccessTier.PREMIUM


def test_multiple_access_keys_are_supported(monkeypatch) -> None:
    first_key = "dani_first"
    second_key = "dani_second"

    monkeypatch.setattr(
        settings,
        "premium_access_key_hashes",
        ",".join(
            [
                hash_access_key(first_key),
                hash_access_key(second_key),
            ]
        ),
    )

    assert resolve_access_tier(second_key) is AccessTier.PREMIUM
