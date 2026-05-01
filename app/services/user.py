from sqlalchemy import select
from app.database.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import generate_access_token
from .base import BaseService
from passlib.context import CryptContext  # type:ignore
from fastapi import HTTPException, status


class UserService(BaseService):
    def __init__(self, model: User, session: AsyncSession):
        self.model = model
        self.session = session
        self.pw_context = CryptContext(schemes=["argon2"])

    def hash_password(self, password: str) -> str:
        return self.pw_context.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.pw_context.verify(password, hashed_password)

    async def _add_user(self, data: dict):
        user = self.model(**data, password_hash=self.pw_context.hash(data["password"]))
        return await self._add(user)

    async def _get_by_eamil(self, email) -> User | None:
        return await self.session.scalar(
            select(self.model).where(self.model.email == email)
        )

    async def _generate_token(self, email, password) -> str:
        user = await self._get_by_eamil(email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="The email is not found"
            )

        if not self.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="The password is wrong"
            )

        return generate_access_token(
            data={
                "user": {
                    "id": str(user.id),
                    "name": user.name,
                }
            }
        )
