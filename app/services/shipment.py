from uuid import UUID
from fastapi import HTTPException, status
from app.core.exceptions import ClientNotAuthorized, EntityNotFound, InvalidToken
from app.database.models import DeliveryPartner, Review, Seller, Shipment, TagName
from app.api.schemas.shipment import (
    ShipmentCreate,
    ShipmentReview,
    ShipmentUpdate,
    ShipmentStatus,
)
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.database.redis import get_shipment_verification_code
from app.services.base import BaseService
from app.services.delivery_partner import DeliveryPartnerService
from app.services.shipment_event import ShipmentEventService
from app.utils import decode_url_safe_token


class ShipmentService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        partner_service: DeliveryPartnerService,
        event_service: ShipmentEventService,
    ):
        super().__init__(Shipment, session)  # type:ignore
        self.partner_service = partner_service
        self.event_service = event_service

    async def get(self, id: UUID) -> Shipment | None:
        shipment = await self._get(id)

        if shipment is None:
            raise EntityNotFound()

        return shipment

    async def add(self, shipment_create: ShipmentCreate, seller: Seller) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            estimated_delivery=datetime.now() + timedelta(days=3),
            seller_id=seller.id,
        )
        partner = await self.partner_service.assign_shipment(new_shipment)

        new_shipment.delivery_partner_id = partner.id

        shipment = await self._add(new_shipment)

        event = await self.event_service.add(
            shipment=shipment,
            location=seller.zip_code,
            status=ShipmentStatus.out_for_delivery,
            description=f"assigned to {partner.name}",
        )

        shipment.timeline.append(event)

        return shipment

    async def update(
        self, id: UUID, shipment_update: ShipmentUpdate, partner: DeliveryPartner
    ) -> Shipment | None:
        shipment = await self.get(id)

        if shipment.delivery_partner_id != partner.id:
            raise ClientNotAuthorized()

        if shipment_update.status == ShipmentStatus.delivered:
            code = get_shipment_verification_code(shipment.id)

            if code != shipment_update.verification_code:
                raise ClientNotAuthorized()

        update = shipment_update.model_dump(
            exclude_none=True,
            exclude={"verification_code"},
        )

        if shipment_update.estimated_delivery:
            shipment.estimated_delivery = shipment_update.estimated_delivery

        if len(update) > 1 or not shipment_update.estimated_delivery:
            await self.event_service.add(
                shipment=shipment,
                **update,
            )

        return await self._update(shipment)




    async def cancel(self, id: UUID, seller: Seller) -> Shipment:
        shipment = await self.get(id)

        if shipment.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authorized",
            )

        event = await self.event_service.add(
            shipment_id=shipment.id, 
            status=ShipmentStatus.cancelled,
        )

        shipment.timeline.append(event)

        return shipment



    async def delete(self, id: UUID) -> None:
        await self._delete(self.get(id))



    async def rate(self, token: str, rating: int, comment: str):
        token_data = decode_url_safe_token(token)

        if token_data is None:
            raise InvalidToken()

        shipment = await self.get(UUID(token_data["id"]))

        new_review = Review(
            rating=rating,
            comment=comment if comment else None,
            shipment_id=shipment.id,
        )

        self.session.add(new_review)

        await self.session.commit()





    async def add_tag(self, id: UUID, tag_name: TagName):
        shipment = await self.get(id)
        shipment.tags.append(await tag_name.tag(self.session))

        return await self._update(shipment)


    async def remove_tag(self, id: UUID, tag_name: TagName):
        shipment = await self.get(id)
        try:
            shipment.tags.remove(await tag_name.tag(self.session))
        except ValueError:
            raise EntityNotFound()
        
        return await self._update(shipment)
