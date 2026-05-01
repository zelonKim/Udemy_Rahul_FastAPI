from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field

from app.database.models import Seller


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class ShipmentBase(BaseModel):
    content: str
    weight: float = Field(le=25, gt=0)
    destination: int


class ShipmentRead(ShipmentBase):
    id: UUID
    seller: Seller
    status: ShipmentStatus
    estimated_delivery: datetime


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentUpdate(BaseModel):
    status: ShipmentStatus | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)
