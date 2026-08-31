from typing import Annotated

from fastapi import APIRouter, Header
from pydantic import BaseModel

from dani_api.access import AccessTier, resolve_access

router = APIRouter(
    prefix="/api/access",
    tags=["access"],
)


class AccessVerificationResponse(BaseModel):
    """Result of validating a DANI access key."""

    valid: bool
    access_tier: AccessTier


@router.get(
    "/verify",
    response_model=AccessVerificationResponse,
)
def verify_access(
    access_key: Annotated[
        str | None,
        Header(alias="X-DANI-Access-Key"),
    ] = None,
) -> AccessVerificationResponse:
    """Verify whether an access key grants premium access."""

    access = resolve_access(access_key)

    return AccessVerificationResponse(
        valid=access.tier is AccessTier.PREMIUM,
        access_tier=access.tier,
    )
