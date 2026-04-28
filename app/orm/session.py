from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session
from typing import Annotated


engine = create_engine(
    url="sqlite:///sqlite.db", echo=True, connect_args={"check_same_thread": False}
)

def create_db_tables():
    # SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)


def get_session():
    with Session(bind=engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
