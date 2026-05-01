from uuid import UUID

from app.database.models import Seller, Shipment
from app.api.schemas.shipment import ShipmentCreate, ShipmentUpdate, ShipmentStatus
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.services.base import BaseService
from app.services.delivery_partner import DeliveryPartnerService


class ShipmentService(BaseService):
    def __init__(self, session: AsyncSession, partner_service: DeliveryPartnerService):
        super().__init__(Shipment, session)  # type:ignore
        self.partner_service = partner_service

    async def get(self, id: UUID) -> Shipment | None:
        return await self._get(id)

    async def add(self, shipment_create: ShipmentCreate, seller: Seller) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now() + timedelta(days=3),
            seller_id=seller.id,
        )
        partner = await self.partner_service.assign_shipment(new_shipment)
        new_shipment.delivery_partner_id = partner.id

        return await self._add(new_shipment)

    async def update(
        self, id: UUID, shipment_update: ShipmentUpdate
    ) -> Shipment | None:
        shipment = await self.get(id)
        if shipment:
            shipment.sqlmodel_update(shipment_update)

        return await self._update(shipment)  # type:ignore

    async def delete(self, id: UUID) -> None:
        await self._delete(self.get(id))
