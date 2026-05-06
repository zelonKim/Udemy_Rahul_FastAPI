from fastapi import HTTPException, status
from sqlalchemy import select, any_, func
from typing import Sequence
from app.api.schemas.delivery_partner import DeliveryPartnerCreate
from app.database.models import DeliveryPartner, Shipment, ShipmentEvent, ShipmentStatus
from app.services.user import UserService


class DeliveryPartnerService(UserService):
    def __init__(
        self,
        session,
        # tasks,
    ):
        super().__init__(
            DeliveryPartner,
            session,
            # tasks,
        )

    async def add(self, delivery_partner: DeliveryPartnerCreate):
        return await self._add_user(delivery_partner.model_dump(), "partner")

    async def get_partner_by_zipcode(self, zipcode: int) -> Sequence[DeliveryPartner]:
        return (
            await self.session.scalars(
                select(DeliveryPartner).where(
                    zipcode == any_(DeliveryPartner.serviceable_zip_codes)
                )
            )
        ).all()

    async def get_active_shipment_count(self, partner_id):
        result = await self.session.execute(
            select(func.count(Shipment.id))
            .join(ShipmentEvent, Shipment.id == ShipmentEvent.shipment_id)
            .where(
                Shipment.delivery_partner_id == partner_id,
                ShipmentEvent.status != ShipmentStatus.delivered,
                ShipmentEvent.status != ShipmentStatus.cancelled,
            )
        )
        return result.scalar() or 0

    async def has_capacity(self, partner: DeliveryPartner):
        active_count = await self.get_active_shipment_count(partner.id)
        return partner.max_handling_capacity > active_count

    async def assign_shipment(self, shipment: Shipment):
        eligible_partners = await self.get_partner_by_zipcode(shipment.destination)

        for partner in eligible_partners:
            if await self.has_capacity(partner):
                shipment.delivery_partner_id = partner.id
                return partner

        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="No delivery partner available",
        )

    async def update(self, partner: DeliveryPartner):
        return await self._update(partner)

    async def token(self, email, password) -> str:
        return await self._generate_token(email, password)
