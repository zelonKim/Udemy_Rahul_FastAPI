from pydantic import BaseModel, EmailStr


class SellerBase(BaseModel):
    name: str
    email: EmailStr



class SellerRead(SellerBase):
    pass


class SellerCreate(SellerBase):
    password: str