from enum import Enum
from random import randint
from pydantic import BaseModel, Field


def random_destination():
    return randint(1, 1000)


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class ShipmentBase(BaseModel):
    content: str = Field(max_length=30)
    weight: float = Field(description="The unit is kilogram.", le=25, gt=0)
    destination: int | None = Field(default_factory=random_destination)


class ShipmentRead(ShipmentBase):
    status: ShipmentStatus


class Order(BaseModel):
    price: int
    title: str
    description: str


class ShipmentCreate(ShipmentBase):
    order: Order


class ShipmentUpdate(BaseModel):
    content: str | None = Field(default=None)
    weight: float | None = Field(default=None, le=25, gt=0)
    destination: int | None = Field(default=None)
    status: ShipmentStatus
