from typing import Any
from fastapi import FastAPI, status, HTTPException
from scalar_fastapi import get_scalar_api_reference

app = FastAPI()


shipments_data = {
    12701: {
         "weight": 2.5,
         "content": "metal chair",
         "status": "delivered",
    },
    12702: {
         "weight": 1.0,
         "content": "books",
         "status": "in transit",
    },
    12703: {
         "weight": 5.5,
         "content": "sofa",
         "status": "pending",
    },
    12704: {
         "weight": 0.5,
         "content": "lamp",
         "status": "delivered",
    },
    12705: {
         "weight": 3.2,
         "content": "bicycle",
         "status": "in transit",
    }
}





@app.get("/shipments")
def get_shipments():
    return shipments_data



@app.get("/shipment/latest")
def get_latest_shipment() -> dict[str, Any]:
    id = max(shipments_data.keys())
    return shipments_data[id]



@app.get("/shipment")
def get_shipment_with_query_params(id: int) -> dict[str, Any]:
    if id not in shipments_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="The given id doesn`t exist.")
    return shipments_data[id]




@app.get("/shipment/{id}")
def get_shipment_with_path(id: int) -> dict[str, Any]:
    if id not in shipments_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="The given id doesn`t exist.")
    return shipments_data[id]
    



@app.get("/shipment/{id}/{field}")
def get_shipment_field(id:int, field:str) -> Any:
    return shipments_data[id][field]
    
    
    
    
    
    
    

    
    
    

@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
    
    
    
    
    
    
    

@app.post("/shipment")
def post_shipment_with_query_params(weight:float, content: str) -> dict[str, Any]:

    if weight > 25:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Maximum weight limit is 25kg."
        )
        
    new_id = max(shipments_data.keys()) + 1 
    
    shipments_data[new_id] = {
        "weight": weight,
        "content": content,
        "status": "placed",
    }
    
    return {"id": new_id}







@app.post("/shipments")
def post_shipments_with_request_body(data: dict[str, Any]) -> dict[str, Any]:
    weight = data['weight']
    content = data['content']

    if weight > 25:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Maximum weight limit is 25kg."
        )
        
    new_id = max(shipments_data.keys()) + 1 
    
    shipments_data[new_id] = {
        "weight": weight,
        "content": content,
        "status": "placed",
    }
    
    return {"id": new_id}