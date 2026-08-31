import hashlib
import secrets
from dataclasses import dataclass
from enum import StrEnum

from dani_api.config import settings


class AccessTier(StrEnum):
    FREE = "free"
    PREMIUM = "premium"


@dataclass(frozen=True)
class AccessContext:
    tier: AccessTier
    key_id: str | None = None


def hash_access_key(access_key: str) -> str:
    """Return the SHA-256 hash for an access key."""
    return hashlib.sha256(access_key.encode("utf-8")).hexdigest()


def resolve_access(
    access_key: str | None,
) -> AccessContext:
    """Resolve access tier and key identity."""
    if access_key is None:
        return AccessContext(
            tier=AccessTier.FREE,
        )

    normalized_key = access_key.strip()

    if not normalized_key:
        return AccessContext(
            tier=AccessTier.FREE,
        )

    candidate_hash = hash_access_key(normalized_key)

    for (
        key_id,
        stored_hash,
    ) in settings.premium_access_key_hashes.items():
        if secrets.compare_digest(
            candidate_hash,
            stored_hash,
        ):
            return AccessContext(
                tier=AccessTier.PREMIUM,
                key_id=key_id,
            )

    return AccessContext(
        tier=AccessTier.FREE,
    )
