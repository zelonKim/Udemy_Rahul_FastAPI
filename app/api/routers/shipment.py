from fastapi import APIRouter, HTTPException, status
from app.database.models import Shipment
from app.api.schemas.shipment import ShipmentCreate, ShipmentUpdate
from ..schemas.dependencies import CurrentSellerDep, ShipmentServiceDep


router = APIRouter(prefix="/shipment", tags=["Shipment"])


@router.get("/{id}", response_model=Shipment)
async def get_shipment(
    id: int,
    service: ShipmentServiceDep,
    seller: CurrentSellerDep,
):
    shipment = await service.get(id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The given id doesn`t exist."
        )
    return shipment


@router.post("/")
async def create_shipment(
    data: ShipmentCreate,
    service: ShipmentServiceDep,
    seller: CurrentSellerDep,
) -> Shipment:
    return await service.add(data)


################################


@router.patch("/", response_model=Shipment)
async def update_shipment(
    id: int,
    data: ShipmentUpdate,
    service: ShipmentServiceDep,
):
    update_data = data.model_dump(exclude_none=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided to update"
        )

    shipment = await service.update(id, update_data)  # type:ignore
    return shipment


@router.delete("/")
async def delete_shipment(
    id: int,
    service: ShipmentServiceDep,
) -> dict[str, str]:
    await service.delete(id)
    return {"detail": f"Shipment with id {id} is deleted."}
