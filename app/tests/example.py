from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import DeliveryPartner, Location, Seller


password_context = CryptContext(schemes=["argon2"])

SELLER = {
    "name": "RainForest",
    "email": "rainforest@xmailg.one",
    "password": "lovetrees",
    "zip_code": 11011,
}
DELIVERY_PARTNER = {
    "name": "PHL",
    "email": "phl@xmailg.one",
    "password": "tough",
    "zip_code": 11011,
    "max_handling_capacity": 5,
    "serviceable_zip_codes": [11011, 11012, 11013, 11014, 11015],
}
SHIPMENT = {
    "content": "Bananas",
    "weight": 1.25,
    "destination": 11011,
    "client_contact_email": "py@xmailg.one",
    "location": 11011,
}


async def create_test_data(session: AsyncSession):
    session.add(
        Seller(
            **SELLER,
            email_verified=True,
            password_hash=password_context.hash(SELLER["password"]),
        )
    )
    session.add(
        DeliveryPartner(
            **DELIVERY_PARTNER,
            email_verified=True,
            password_hash=password_context.hash(DELIVERY_PARTNER["password"]),
            servicable_locations=[
                Location(zip_code=zip_code)
                for zip_code in DELIVERY_PARTNER["serviceable_zip_codes"]
            ],
        )
    )

    await session.commit()
