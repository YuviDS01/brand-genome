from datetime import datetime
from uuid import UUID

from app.schemas.common import ORMBase


class SocialAccountOut(ORMBase):
    id: UUID
    platform: str
    username: str | None = None
    url: str
    followers: int | None = None
    following: int | None = None
    engagement: float | None = None
    posting_frequency: str | None = None
    last_checked: datetime | None = None


class DigitalPresenceOut(ORMBase):
    """
    Not a 1:1 table — assembled by the Dashboard API from brand_identity
    (official website) + social_accounts (Section 14).
    """

    official_website: str | None = None
    social_accounts: list[SocialAccountOut] = []
