from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.database.models import Seller, ShipmentEvent, Tag, TagName


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"


class ShipmentBase(BaseModel):
    content: str
    weight: float = Field(le=25, gt=0)
    destination: int






class TagRead(BaseModel):
    name: TagName
    instruction: str
    


class ShipmentRead(ShipmentBase):
    id: UUID
    timeline: list[ShipmentEvent]
    estimated_delivery: datetime
    tags: list[Tag]






class ShipmentCreate(ShipmentBase):
    client_contact_email: EmailStr
    client_contact_phone: str | None = Field(default=None)


class ShipmentUpdate(BaseModel):
    location: int | None = Field(default=None)
    status: ShipmentStatus | None = Field(default=None)
    description: str | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)
    verification_code: str | None = Field(default=None)


class ShipmentReview(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None)
