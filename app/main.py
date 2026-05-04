from fastapi import BackgroundTasks, FastAPI
from fastapi.concurrency import asynccontextmanager
from scalar_fastapi import get_scalar_api_reference
from app.database.session import create_db_tables
from app.api.router import main_router



@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI(lifespan=lifespan_handler)

app.include_router(main_router)




###################################


# db = Database()


# @app.get("/shipment/{id}", response_model=ShipmentRead)
# async def get_shipment(id: int, session: SessionDep):
#     shipment = await session.get(Shipment, id)

#     if shipment is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="The given id doesn`t exist."
#         )
#     return shipment


# # @app.get("/shipment/{id}", response_model=ShipmentRead)
# # def get_shipment(id: int):

# #     shipment = db.get(id)

# #     if shipment is None:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND, detail="The given id doesn`t exist."
# #         )
# #     return shipment


# ##################################


# @app.post("/shipment", response_model=None)
# def create_shipment(shipment: ShipmentCreate, session: SessionDep) -> dict[str, Any]:
#     new_shipment = Shipment(
#         **shipment.model_dump(),
#         status=ShipmentStatus.placed,
#         estimated_delivery=datetime.now() + timedelta(days=3),
#     )
#     session.add(new_shipment)
#     session.commit()
#     session.refresh(new_shipment)

#     return {"id": new_shipment.id}


# # @app.post("/shipment", response_model=None)
# # def create_shipment(shipment: ShipmentCreate) -> dict[str, Any]:
# #     new_id = db.create(shipment)
# #     return {"id": new_id}


# ##################################


# @app.patch("/shipment", response_model=ShipmentRead)
# def update_shipment(id: int, data: ShipmentUpdate, session: SessionDep):
#     update_data = data.model_dump(exclude_none=True)

#     if not update_data:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided to update"
#         )

#     shipment = session.get(Shipment, id)
#     if shipment:
#         shipment.sqlmodel_update(update_data)

#     session.add(shipment)
#     session.commit()
#     session.refresh(shipment)

#     return shipment


# # @app.patch("/shipment", response_model=ShipmentRead)
# # def update_shipment(
# #     id: int,
# #     shipment: ShipmentUpdate,
# # ):
# #     shipment = db.update(id, shipment)
# #     return shipment


# ##################################


# @app.delete("/shipment")
# def delete_shipment(id: int, session: SessionDep) -> dict[str, str]:
#     session.delete(session.get(Shipment, id))
#     session.commit()
#     return {"detail": f"Shipment with id {id} is deleted."}


# # @app.delete("/shipment")
# # def delete_shipment(id: int) -> dict[str, str]:
# #     db.delete(id)
# #     return {"detail": f"Shipment with id {id} is deleted."}


##################################


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
