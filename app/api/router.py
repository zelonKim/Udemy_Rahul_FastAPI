from fastapi import APIRouter
from .routers import shipment, seller, delivery_partner

main_router = APIRouter()

main_router.include_router(shipment.router)
main_router.include_router(seller.router)
main_router.include_router(delivery_partner.router)