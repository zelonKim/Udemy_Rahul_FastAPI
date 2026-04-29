from app.database.models import Shipment
from app.api.schemas.shipment import ShipmentCreate, ShipmentUpdate, ShipmentStatus
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta


class ShipmentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Shipment | None:
        return await self.session.get(Shipment, id)



    async def add(self, shipment_create: ShipmentCreate) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now() + timedelta(days=3),
        )
        self.session.add(new_shipment)
        await self.session.commit()
        await self.session.refresh(new_shipment)

        return new_shipment



    async def update(self, id: int, shipment_update: ShipmentUpdate) -> Shipment | None:
        shipment = await self.get(id)
        if shipment:
            shipment.sqlmodel_update(shipment_update)

        self.session.add(shipment)
        await self.session.commit()
        await self.session.refresh(shipment)

        return shipment



    async def delete(self, id: int) -> None:
        await self.session.delete(await self.get(id))
        await self.session.commit()



