from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import User


class UserService(BaseModel):
    async def get_user_by_oidc(
        self,
        *,
        oidc_sub: str,
        oidc_iss: str,
        db_session: AsyncSession,
    ) -> Optional[User]:
        result = await db_session.execute(
            select(User).where(
                User.oidc_sub == oidc_sub,
                User.oidc_iss == oidc_iss,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(
        self,
        *,
        user_id: UUID,
        db_session: AsyncSession,
    ) -> Optional[User]:
        return await db_session.get(User, user_id)

    async def seen_user(
        self,
        *,
        user: User,
        db_session: AsyncSession,
    ) -> None:
        user.last_seen = datetime.now(timezone.utc)
        db_session.add(user)

    async def upsert_user_by_oidc(
        self,
        *,
        oidc_sub: str,
        oidc_iss: str,
        email: Optional[str] = None,
        display_name: Optional[str] = None,
        preferred_username: Optional[str] = None,
        db_session: AsyncSession,
    ) -> User:
        user = await self.get_user_by_oidc(
            oidc_sub=oidc_sub,
            oidc_iss=oidc_iss,
            db_session=db_session,
        )

        if user:
            user.email = email or user.email
            user.display_name = display_name or user.display_name
            user.preferred_username = preferred_username or user.preferred_username
            db_session.add(user)
            return user

        user = User(
            oidc_sub=oidc_sub,
            oidc_iss=oidc_iss,
            email=email,
            display_name=display_name,
            preferred_username=preferred_username,
        )
        db_session.add(user)
        return user
