from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from app.database.models import Shipment
from app.api.schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate
from ..schemas.dependencies import (
    CurrentPartnerDep,
    CurrentSellerDep,
    ShipmentServiceDep,
)


router = APIRouter(prefix="/shipment", tags=["Shipment"])


@router.get("/{id}", response_model=ShipmentRead)
async def get_shipment(
    id: UUID,
    service: ShipmentServiceDep,
):
    shipment = await service.get(id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The given id doesn`t exist."
        )
    return shipment


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


@router.delete("/cancel")
async def cancel_shipment(
    id: UUID,
    seller: CurrentSellerDep,
    service: ShipmentServiceDep,
):
    return await service.cancel(id, seller)
