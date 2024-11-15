from pydantic import BaseModel
from datetime import datetime

class ClientCreate(BaseModel):
    name: str
    email: str

class ClientUpdate(BaseModel):
    name: str
    email: str

class ClientResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True