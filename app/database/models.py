from enum import Enum
from pydantic import EmailStr
from sqlmodel import Column, SQLModel, Field, Relationship, select
from datetime import datetime
from uuid import uuid4, UUID
from sqlalchemy.dialects import postgresql
from sqlalchemy import ARRAY, INTEGER
from sqlalchemy.ext.asyncio import AsyncSession


class ShipmentTag(SQLModel, table=True):
    __tablename__ = "shipment_tag"

    tag_id: UUID = Field(
        foreign_key="tag.id",
        primary_key=True,
    )

    shipment_id: UUID = Field(
        foreign_key="shipment.id",
        primary_key=True,
    )


#######################################


class TagName(str, Enum):
    EXPRESS = "express"
    STANDARD = "standard"
    FRAGILE = "fragile"
    HEAVY = "heavy"
    INTERNATIONAL = "international"
    DOMESTIC = "domestic"
    TEMPERATURE_CONTROLLED = "temperature_controlled"
    GIFT = "gift"
    RETURN = "return"
    DOCUMENTS = "documents"

    async def tag(self, session: AsyncSession):
        return await session.scalar(select(Tag).where(Tag.name == self.value))


class Tag(SQLModel, table=True):
    __tablename__ = "tag"

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )

    name: TagName

    instruction: str

    shipments: list["Shipment"] = Relationship(
        back_populates="tags",
        link_model=ShipmentTag,
        sa_relationship_kwargs={"lazy": "immediate"},
    )


#######################################


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))

    client_contact_email: EmailStr

    client_contact_phone: str | None

    content: str
    weight: float = Field(le=25)
    destination: int
    estimated_delivery: datetime

    status: ShipmentStatus = Field(default=ShipmentStatus.placed)

    timeline: list["ShipmentEvent"] = Relationship(
        back_populates="shipment",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    seller_id: UUID = Field(foreign_key="seller.id")
    seller: "Seller" = Relationship(
        back_populates="shipments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    delivery_partner_id: UUID = Field(foreign_key="delivery_partner.id")
    delivery_partner: "DeliveryPartner" = Relationship(
        back_populates="shipments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    review: "Review" = Relationship(back_populates="shipment")

    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.now)
    )

    tags: list[Tag] = Relationship(
        back_populates="shipments",
        link_model=ShipmentTag,
        sa_relationship_kwargs={"lazy": "immediate"},
    )


##########################################


class ShipmentEvent(SQLModel, table=True):
    __tablename__ = "shipment_event"

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))

    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.now)
    )

    location: int | None
    status: ShipmentStatus | None
    description: str | None

    shipment_id: UUID = Field(foreign_key="shipment.id")

    shipment: Shipment = Relationship(
        back_populates="timeline",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class User(SQLModel):
    name: str
    email: EmailStr
    email_verified: bool = Field(default=False)
    password_hash: str


class Seller(User, table=True):
    __tablename__ = "seller"

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))

    address: str | None = Field(default=None)
    zip_code: int | None = Field(default=None)

    shipments: list[Shipment] = Relationship(
        back_populates="seller",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.now)
    )


class ServiceableLocation(SQLModel, table=True):
    __tablename__ = "serviceable_location"

    partner_id: UUID = Field(foreign_key="delivery_partner.id", primary_key=True)

    location_id: int = Field(foreign_key="location.zip_code", primary_key=True)


class DeliveryPartner(User, table=True):
    __tablename__ = "delivery_partner"

    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True))

    serviceable_locations: list["Location"] = Relationship(
        back_populates="delivery_partners",
        link_model=ServiceableLocation,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    max_handling_capacity: int

    shipments: list[Shipment] = Relationship(
        back_populates="delivery_partner",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.now)
    )


class Location(SQLModel, table=True):
    __tablename__ = "location"

    zip_code: int = Field(primary_key=True)

    delivery_partners: list["DeliveryPartner"] = Relationship(
        back_populates="serviceable_locations",
        link_model=ServiceableLocation,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Review(SQLModel, table=True):
    __tablename__ = "review"

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )

    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    rating: int = Field(ge=1, le=5)

    comment: str | None = Field(default=None)

    shipment_id: UUID = Field(foreign_key="shipment.id")

    shipment: Shipment = Relationship(
        back_populates="review",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


#########################################


class Order(SQLModel, table=True):
    product_id: UUID = Field(foreign_key="product.id", primary_key=True)
    container_id: UUID = Field(foreign_key="container.id", primary_key=True)

    product: "Product" = Relationship(back_populates="orders")
    container: "Container" = Relationship(back_populates="orders")

    created_at: datetime
    quantity: int = Field(default=1)


class Product(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    title: str
    price: float
    weight: float
    description: str

    orders: list["Order"] = Relationship(back_populates="product")


class Container(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    status: str
    weight: float
    destination: str

    orders: list["Order"] = Relationship(back_populates="container")


#########################################
