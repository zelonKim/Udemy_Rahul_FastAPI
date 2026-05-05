from uuid import UUID
from app.database.models import DeliveryPartner, Seller
from app.database.redis import is_jti_blacklisted
from app.services.delivery_partner import DeliveryPartnerService
from app.services.shipment import ShipmentService
from app.services.seller import SellerService
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks, Depends, HTTPException, status
from app.database.session import get_session
from app.core.security import oauth2_scheme_seller, oauth2_scheme_partner
from app.services.shipment_event import ShipmentEventService
from app.utils import decode_access_token


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def _get_access_token(
    token: str,
) -> dict:
    data = decode_access_token(token)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Access Token."
        )

    if await is_jti_blacklisted(data["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Blacklisted Access Token"
        )

    return data


#####################################


async def get_seller_access_token(token: Annotated[str, Depends(oauth2_scheme_seller)]):
    return await _get_access_token(token)


async def get_current_seller(
    token_data: Annotated[dict, Depends(get_seller_access_token)], session: SessionDep
):
    seller = await session.get(Seller, UUID(token_data["user"]["id"]))

    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized"
        )

    return seller


CurrentSellerDep = Annotated[Seller, Depends(get_current_seller)]


#####################################


async def get_partner_access_token(
    token: Annotated[str, Depends(oauth2_scheme_partner)],
):
    return await _get_access_token(token)


async def get_current_partner(
    token_data: Annotated[dict, Depends(get_partner_access_token)], session: SessionDep
):
    partner = await session.get(DeliveryPartner, UUID(token_data["user"]["id"]))

    if partner is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized"
        )

    return partner


CurrentPartnerDep = Annotated[DeliveryPartner, Depends(get_current_partner)]


#####################################


async def get_shipment_service(session: SessionDep, tasks: BackgroundTasks):
    return ShipmentService(
        session, DeliveryPartnerService(session), ShipmentEventService(session, tasks)
    )


ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]


#####################################


def get_seller_service(session: SessionDep, tasks: BackgroundTasks):
    return SellerService(session, tasks)


SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]


#####################################


def get_delivery_partner_service(session: SessionDep, tasks: BackgroundTasks):
    return DeliveryPartnerService(session, tasks)


PartnerServiceDep = Annotated[
    DeliveryPartnerService,
    Depends(get_delivery_partner_service),
]
