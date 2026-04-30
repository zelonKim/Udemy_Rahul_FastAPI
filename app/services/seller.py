from fastapi import HTTPException, status, HTTPException
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas.seller import SellerCreate
from app.database.models import Seller
from passlib.context import CryptContext  # type:ignore
import hashlib

from app.utils import generate_access_token


class SellerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.pw_context = CryptContext(schemes=["bcrypt"])


    def hash_password(self, password: str) -> str:
        return self.pw_context.hash(hashlib.sha256(password.encode()).hexdigest())


    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.pw_context.verify(
            hashlib.sha256(password.encode()).hexdigest(), hashed_password
        )


    async def add(self, credentials: SellerCreate) -> Seller:
        seller = Seller(
            **credentials.model_dump(exclude={"password"}),
            password_hash=self.hash_password(credentials.password),
        )
        self.session.add(seller)
        await self.session.commit()
        await self.session.refresh(seller)

        return seller



    async def token(self, email, password) -> str:
        result = await self.session.execute(select(Seller).where(Seller.email == email))
        seller = result.scalar()

        await self.session.get(Seller, seller.id)  # type:ignore

        if seller is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="The email is not found"
            )

        if not self.verify_password(password, seller.password_hash):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="The password is wrong"
            )

        token = generate_access_token(
            data={
                "user": {
                    "id": seller.id,
                    "name": seller.name,
                }
            }
        )
        return token
