from datetime import timedelta
from uuid import UUID

from sqlalchemy import select
from app.database.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.notification import NotificationService
from app.utils import (
    decode_url_safe_token,
    generate_access_token,
    generate_url_safe_token,
)
from app.worker.tasks import send_email_with_template
from .base import BaseService
from passlib.context import CryptContext  # type:ignore
from fastapi import BackgroundTasks, HTTPException, status
from app.config import app_settings


class UserService(BaseService):
    def __init__(
        self,
        model: User,
        session: AsyncSession,
        # tasks: BackgroundTasks,
    ):
        self.model = model
        self.session = session
        # self.notification_service = NotificationService(tasks)
        self.pw_context = CryptContext(schemes=["argon2"])

    def hash_password(self, password: str) -> str:
        return self.pw_context.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.pw_context.verify(password, hashed_password)

    async def _add_user(self, data: dict, router_prefix: str):
        user = self.model(**data, password_hash=self.pw_context.hash(data["password"]))

        user = await self._add(user)

        token = generate_url_safe_token(
            {
                "id": str(user.id),
            }
        )

        # await self.notification_service.send_email_with_template(
        send_email_with_template.delay(
            recipients=[user.email],
            subject="Verify Your Account with FastShip",
            context={
                "username": user.name,
                "verification_url": f"http://{app_settings.APP_DOMAIN}/{router_prefix}/verify?token={token}",
            },
            template_name="mail_email_verify.html",
        )

        return user
    
    

    async def verify_email(self, token: str):
        token_data = decode_url_safe_token(token)

        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token"
            )

        user = await self._get(UUID(token_data["id"]))
        user.email_verified = True

        await self._update(user)



    async def _get_by_email(self, email) -> User | None:
        return await self.session.scalar(
            select(self.model).where(self.model.email == email)
        )



    async def _generate_token(self, email, password) -> str:
        user = await self._get_by_email(email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="The email is not found"
            )

        if not self.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="The password is wrong"
            )

        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email is not verified",
            )

        return generate_access_token(
            data={
                "user": {
                    "id": str(user.id),
                    "name": user.name,
                }
            }
        )



    async def send_password_reset_link(self, email, router_prefix):
        user = await self._get_by_email(email)

        token = generate_url_safe_token({"id": str(user.id)}, salt="password-reset")

        # await self.notification_service.send_email_with_template(
        send_email_with_template.delay(
            recipients=[user.email],
            subject="Account Password Reset",
            context={
                "username": user.name,
                "reset_url": f"http://{app_settings.APP_DOMAIN}{router_prefix}/reset_password_form?token={token}",
            },
            template_name="mail_password_reset.html",
        )
        

    async def reset_password(self, token: str, password: str) -> bool:
        token_data = decode_url_safe_token(
            token,
            salt="password-reset",
            expiry=timedelta(days=1),
        )

        if not token_data:
            return False

        user = await self._get(UUID(token_data["id"]))

        user.password_hash = self.pw_context.hash(password)

        await self._update(user)

        return True
