from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database.models import Shipment, ShipmentStatus, TagName
from app.api.schemas.shipment import (
    ShipmentCreate,
    ShipmentRead,
    ShipmentReview,
    ShipmentUpdate,
)
from app.utils import TEMPLATE_DIR
from ..schemas.dependencies import (
    CurrentPartnerDep,
    CurrentSellerDep,
    SessionDep,
    ShipmentServiceDep,
)
from app.config import app_settings


router = APIRouter(prefix="/shipment", tags=["Shipment"])


templates = Jinja2Templates(TEMPLATE_DIR)


@router.get("/", response_model=ShipmentRead)
async def get_shipment(
    id: UUID,
    service: ShipmentServiceDep,
    # seller: CurrentSellerDep,
):
    # return {}
    return await service.get(id)


@router.get("/track")
async def get_tracking(request: Request, id: UUID, service: ShipmentServiceDep):
    shipment = await service.get(id)

    context = shipment.model_dump()
    context["status"] = ShipmentStatus.placed
    context["partner"] = shipment.delivery_partner.name
    context["timeline"] = shipment.timeline
    context["timeline"].reverse()

    return templates.TemplateResponse(
        request=request,
        name="track.html",
        context=context,
    )


@router.post("/", response_model=ShipmentRead)
async def create_shipment(
    shipment: ShipmentCreate,
    service: ShipmentServiceDep,
    seller: CurrentSellerDep,
) -> Shipment:
    return await service.add(shipment, seller)


################################


@router.patch("/", response_model=ShipmentRead)
async def update_shipment(
    id: UUID,
    shipment_update: ShipmentUpdate,
    partner: CurrentPartnerDep,
    service: ShipmentServiceDep,
):
    update = shipment_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided to update"
        )

    return await service.update(id, shipment_update, partner)





@router.get("/tagged", response_model=list[ShipmentRead])
async def get_shipments_with_tag(tag_name: TagName, session: SessionDep):
    tag = await tag_name.tag(session)
    return tag.shipments


@router.get("/tag", response_model=ShipmentRead)
async def add_tag_to_shipment(
    id: UUID,
    tag_name: TagName,
    service: ShipmentServiceDep,
):
    return await service.add_tag(id, tag_name)


@router.delete("/tag", response_model=ShipmentRead)
async def remove_tag_from_shipment(
    id: UUID,
    tag_name: TagName,
    service: ShipmentServiceDep,
):
    return await service.remove_tag(id, tag_name)





@router.delete("/cancel")
async def cancel_shipment(
    id: UUID,
    seller: CurrentSellerDep,
    service: ShipmentServiceDep,
):
    return await service.cancel(id, seller)


@router.get("/review")
async def get_review(request: Request, token: str):
    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={
            "review_url": f"http://{app_settings.APP_DOMAIN}/shipment/review?token={token}"
        },
    )


@router.post("/review")
async def submit_review(
    token: str,
    rating: Annotated[int, Form(ge=1, le=5)],
    comment: Annotated[str | None, Form()],
    service: ShipmentServiceDep,
):
    await service.rate(token, rating, comment)
    return {"detail": "Review Submitted"}
