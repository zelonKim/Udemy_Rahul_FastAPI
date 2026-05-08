# from app.tests.conftest import test_id
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest
from app.tests import example


# @pytest.mark.asyncio
# async def test_app(client: AsyncClient):
#     response = await client.get("/")

#     await client.get("/shipment?id=030161a3-0796-4f3e-ab86-40130e6ebe7d")

#     assert response.status_code == 200



async def test_seller_login(client: AsyncClient):
    response = await client.post(
        "/seller/token",
        data={
            "grant_type": "password",
            "username": example.SELLER["email"],
            "password": example.SELLER["password"],
        },
    )
    
    print(response.json())
