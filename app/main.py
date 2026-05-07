from datetime import datetime
from time import perf_counter
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response, status
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
)
from scalar_fastapi import get_scalar_api_reference
from app.core.exceptions import add_exception_handlers
from app.database.session import create_db_tables
from app.api.router import main_router
from app.utils import APP_DIR
from app.worker.tasks import add_log, send_mail
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI(lifespan=lifespan_handler)

app.include_router(main_router)


########################################


add_exception_handlers(app)


@app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error_handler(request, exception):
    return JSONResponse(
        content={"error": f"{exception}"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )









########################################







@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    start = perf_counter()

    response: Response = await call_next(request)

    end = perf_counter()

    time_take = round(end - start, 2)

    add_log.delay(
        f"{request.method} {request.url} ({response.status_code}) {time_take}s"
    )

    return response



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_methods=["*"],
)




############################################


# @app.get("/test")
# def test():
#     send_mail.delay(
#         recipients=["ksz1860@naver.com"],
#         subject="Test Mail",
#         body="Hello"
#     )
#     now = datetime.now()
#     background_task.delay(
#         f"Background Task {now.second}",
#         data={
#             "min": now.minute,
#             "sec": now.second,
#         },
#     )


class UpperResponse(Response):
    def __init__(
        self,
        content=None,
        status_code=200,
        headers=None,
        media_type=None,
        background=None,
    ):
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content):
        content = content.upper()
        return super().render(content)


@app.get(
    "/custom",
    # response_model=dict[str, datetime],
    # response_class=JSONResponse,
    # response_class=HTMLResponse,
    # response_class=FileResponse,
    # response_class=RedirectResponse,
    response_class=UpperResponse,
)
def get_custom_response():
    # return {
    #     "timestamp": datetime.now(),
    # }

    # return HTMLResponse(
    #     content=f"""<body>
    #         <h1>Shipment</h1>
    #         <h2>{datetime.now()}</h2>
    #     </body>"""
    # )

    # return FileResponse(APP_DIR / "file.txt")

    # return RedirectResponse(url="http://localhost:8000/custom-new")

    return "sample shipment"


@app.get("/custom-new")
def get_new_data():
    return "NEW CUSTOM RESPONSE"


###################################################


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
