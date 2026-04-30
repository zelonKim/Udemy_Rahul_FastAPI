from app.database.models import Seller
from app.services.shipment import ShipmentService
from app.services.seller import SellerService
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from app.database.session import get_session
from app.core.security import oauth2_scheme
from app.utils import decode_access_token


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_access_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    data = decode_access_token(token)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Access Token."
        )

    return data



async def get_current_seller(
    token_data: Annotated[dict, Depends(get_access_token)], session: SessionDep
):
    return await session.get(Seller, token_data["user"]["id"])


CurrentSellerDep = Annotated[Seller, Depends(get_current_seller)]




#############################



async def get_shipment_service(session: SessionDep):
    return ShipmentService(session)

ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]


#############################


def get_seller_service(session: SessionDep):
    return SellerService(session)

SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]

