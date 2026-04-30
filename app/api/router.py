from fastapi import APIRouter
from .routers import shipment, seller

main_router = APIRouter()

main_router.include_router(shipment.router)
main_router.include_router(seller.router)
