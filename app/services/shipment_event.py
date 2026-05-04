from sqlmodel import select
from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from app.services.base import BaseService
from app.services.notification import NotificationService


class ShipmentEventService(BaseService):
    def __init__(self, session, tasks):
        super().__init__(ShipmentEvent, session)
        self.notification_service = NotificationService(tasks)

    async def add(
        self,
        shipment: Shipment,
        location: int | None = None,
        status: ShipmentStatus | None = None,
        description: str | None = None,
    ) -> ShipmentEvent:

        # ✅ 필요할 때만 DB 조회
        if location is None or status is None:
            last_event = await self.get_latest_event(shipment)

            if last_event is None:
                raise Exception("First event requires location and status")

            location = location or last_event.location
            status = status or last_event.status

        new_event = ShipmentEvent(
            shipment_id=shipment.id,
            location=location,
            status=status,
            description=description
            if description
            else self._generate_description(status, location),
        )

        await self._notify(shipment, status)

        return await self._add(new_event)


    async def get_latest_event(self, shipment):
        result = await self.session.execute(
            select(ShipmentEvent)
            .where(ShipmentEvent.shipment_id == shipment.id)
            .order_by(ShipmentEvent.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()



    def _generate_description(self, status: ShipmentStatus, location: int):
        match status:
            case ShipmentStatus.placed:
                return "assigned delivery partner"
            case ShipmentStatus.out_for_delivery:
                return "shipment out for delivery"
            case ShipmentStatus.delivered:
                return "Successfully delivered"
            case ShipmentStatus.cancelled:
                return "cancelled by seller"
            case _:
                return f"scanned at {location}"



    async def _notify(self, shipment: Shipment, status: ShipmentStatus):
        match status:
            case ShipmentStatus.placed:
                await self.notification_service.send_email_with_template(
                    recipients=[shipment.client_contact_email],
                    subject="Your Order is Shipped.",
                    context={
                        "seller": shipment.seller.name,
                        "partner": shipment.delivery_partner.name,
                        "id": shipment.id,
                    },
                    template_name="mail_placed.html",
                )

            case ShipmentStatus.out_for_delivery:
                await self.notification_service.send_email(
                    recipients=[shipment.client_contact_email],
                    subject="Your Order is Shipped",
                    body=f"Your order with {shipment.seller.name} seller is picked up by {shipment.delivery_partner.name} delivery partner",
                )

            case ShipmentStatus.delivered:
                await self.notification_service.send_email(
                    recipients=[shipment.client_contact_email],
                    subject="Your Order is Arriving",
                    body="Our delivery executive is on their way to delivery your order. please ensure you are available to get the same.",
                )
