from enum import Enum
from typing import Any
from fastapi import FastAPI, status, HTTPException
from scalar_fastapi import get_scalar_api_reference
from app.schemas import ShipmentCreate, ShipmentRead, ShipmentStatus, ShipmentUpdate


app = FastAPI()


shipments_data = {
    12701: {
        "weight": 2.5,
        "content": "metal chair",
        "status": "delivered",
        "destination": 123,
    },
    12702: {
        "weight": 1.0,
        "content": "books",
        "status": "in_transit",
        "destination": 456,
    },
    12703: {
        "weight": 5.5,
        "content": "sofa",
        "status": "delivered",
        "destination": 789,
    },
    12704: {
        "weight": 0.5,
        "content": "lamp",
        "status": "delivered",
        "destination": 321,
    },
    12705: {
        "weight": 3.2,
        "content": "bicycle",
        "status": "in_transit",
        "destination": 654,
    },
}


@app.get("/shipments")
def get_shipments():
    return shipments_data


@app.get("/shipment/latest")
def get_latest_shipment() -> dict[str, Any]:
    id = max(shipments_data.keys())
    return shipments_data[id]


@app.get("/shipment", response_model=ShipmentRead)
def get_shipment_with_query_params(id: int):
    if id not in shipments_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The given id doesn`t exist."
        )
    return shipments_data[id]


@app.get("/shipment/{id}")
def get_shipment_with_path(id: int) -> dict[str, Any]:
    if id not in shipments_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The given id doesn`t exist."
        )
    return shipments_data[id]


@app.get("/shipment/{id}/{field}")
def get_shipment_field(id: int, field: str) -> Any:
    return shipments_data[id][field]


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )


@app.post("/shipment")
def post_shipment_with_query_params(
    weight: float, content: str, destination: int
) -> dict[str, Any]:

    if weight > 25:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Maximum weight limit is 25kg.",
        )

    new_id = max(shipments_data.keys()) + 1

    shipments_data[new_id] = {
        "content": content,
        "weight": weight,
        "destination": destination,
        "status": "placed",
    }

    return {"id": new_id}


@app.post("/shipments", response_model=None)
def post_shipments_with_request_body(data: ShipmentCreate) -> dict[str, Any]:

    new_id = max(shipments_data.keys()) + 1

    shipments_data[new_id] = {**data.model_dump(), "id": new_id, "status": "placed"}

    return {"id": new_id}


@app.put("/shipment", response_model=ShipmentRead)
def update_shipment(
    id: int, content: str, weight: float, status: str
) -> dict[str, Any]:
    shipments_data[id] = {"content": content, "weight": weight, "status": status}
    return shipments_data[id]


@app.patch("/shipment")
def partial_update_shipment_with_query_params(
    id: int,
    content: str | None = None,
    weight: float | None = None,
    status: ShipmentStatus | None = None,
):
    shipment = shipments_data[id]

    if content:
        shipment["content"] = content

    if weight:
        shipment["weight"] = weight

    if status:
        shipment["status"] = status

    shipments_data[id] = shipment

    return shipment


@app.patch("/shipments", response_model=ShipmentRead)
def partial_update_shipment_with_request_body(
    id: int,
    body: ShipmentUpdate,
):
    shipment = shipments_data[id]
    shipment.update(body.model_dump(exclude_none=True))
    return shipment


@app.delete("/shipment")
def delete_shipment(id: int) -> dict[str, str]:
    shipments_data.pop(id)
    return {"detail": f"Shipment with id {id} is deleted."}
