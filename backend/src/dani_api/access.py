import hashlib
import secrets
from enum import StrEnum

from dani_api.config import settings


class AccessTier(StrEnum):
    FREE = "free"
    PREMIUM = "premium"


def hash_access_key(access_key: str) -> str:
    """Return a SHA-256 hex digest for an access key"""
    return hashlib.sha256(access_key.encode("utf-8")).hexdigest()


def resolve_access_tier(access_key: str | None) -> AccessTier:
    if access_key is None:
        return AccessTier.FREE

    normalized_key = access_key.strip()

    if not normalized_key:
        return AccessTier.FREE

    candidate_hash = hash_access_key(normalized_key)

    for stored_hash in settings.premium_access_key_hash_set:
        if secrets.compare_digest(candidate_hash, stored_hash):
            return AccessTier.PREMIUM

    return AccessTier.FREE
