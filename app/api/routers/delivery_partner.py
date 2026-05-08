from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.tag import APITag
from app.database.redis import add_jti_to_blacklist
from ..schemas.dependencies import (
    CurrentPartnerDep,
    PartnerServiceDep,
    SellerServiceDep,
    get_partner_access_token,
)
from ..schemas.delivery_partner import (
    DeliveryPartnerCreate,
    DeliveryPartnerRead,
    DeliveryPartnerUpdate,
)


router = APIRouter(prefix="/partner", tags=[APITag.PARTNER])


@router.get("/verify")
async def verify_partner_email(token: str, service: SellerServiceDep):
    await service.verify_email(token)
    return {"detail": "Account is verified"}


@router.post("/signup", response_model=DeliveryPartnerRead)
async def register_delivery_partner(
    delivery_partner: DeliveryPartnerCreate,
    service: PartnerServiceDep,
):
    return await service.add(delivery_partner)


@router.post("/token")
async def login_delivery_partner(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: PartnerServiceDep,
):
    token = await service.token(request_form.username, request_form.password)
    return {"access_token": token, "type": "jwt"}


@router.post("/", response_model=DeliveryPartnerRead)
async def update_delivery_partner(
    partner_update: DeliveryPartnerUpdate,
    partner: CurrentPartnerDep,
    service: PartnerServiceDep,
):
    update_data = partner_update.model_dump(exclude_none=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided to update"
        )

    return await service.update(partner.sqlmodel_update(update_data))


@router.get("/logout")
async def logout_delivery_partner(
    token_data: Annotated[dict, Depends(get_partner_access_token)],
):
    await add_jti_to_blacklist(token_data["jti"])
    return {"detail": "Successfully logged out"}
