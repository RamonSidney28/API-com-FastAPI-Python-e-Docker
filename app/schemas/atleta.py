from pydantic import BaseModel
from typing import Optional

class AtletaBase(BaseModel):
    nome: str
    cpf: str
    centro_treinamento: str
    categoria: str

class AtletaCreate(AtletaBase):
    pass

class AtletaResponse(AtletaBase):
    id: int
    
    class Config:
        from_attributes = True

class AtletaUpdate(BaseModel):
    nome: Optional[str] = None
    centro_treinamento: Optional[str] = None
    categoria: Optional[str] = None
