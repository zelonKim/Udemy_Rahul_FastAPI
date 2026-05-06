from random import randint

from sqlmodel import select
from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from app.database.redis import add_shipment_verification_code
from app.services.base import BaseService
from app.services.notification import NotificationService
from app.config import app_settings
from app.utils import generate_url_safe_token
from app.worker.tasks import send_email_with_template, send_sms


class ShipmentEventService(BaseService):
    def __init__(
        self,
        session,
        # tasks,
    ):
        super().__init__(ShipmentEvent, session)
        # self.notification_service = NotificationService(tasks)

    async def add(
        self,
        shipment: Shipment,
        location: int | None = None,
        status: ShipmentStatus | None = None,
        description: str | None = None,
    ) -> ShipmentEvent:

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
                # await self.notification_service.send_email_with_template(
                send_email_with_template.delay(
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
                code = randint(100_000, 999_999)
                await add_shipment_verification_code(shipment.id, str(code))

                if shipment.client_contact_phone:
                    # self.notification_service.send_sms(
                    send_sms.delay(
                        to=shipment.client_contact_phone,
                        body=f"Hello, {code} is Your verification code.",
                    )
                else:
                    # await self.notification_service.send_email_with_template(
                    send_email_with_template.delay(
                        recipients=[shipment.client_contact_email],
                        subject="Your verification code",
                        context={
                            "verification_code": code,
                        },
                        template_name="mail_out_for_delivery.html",
                    )

            case ShipmentStatus.delivered:
                token = generate_url_safe_token({"id": str(shipment.id)})

                # await self.notification_service.send_email_with_template(
                send_email_with_template.delay(
                    recipients=[shipment.client_contact_email],
                    subject="Your Order is Delivered",
                    context={
                        "seller": shipment.seller.name,
                        "review_url": f"http://{app_settings.APP_DOMAIN}/shipment/review?token={token}",
                    },
                    template_name="mail_delivered.html",
                )
