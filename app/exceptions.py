from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

class IntegrityException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=303,
            detail=detail,
            headers={"Location": "/atletas"}
        )

def integrity_exception_handler(request, exc: IntegrityError):
    if "cpf" in str(exc).lower():
        cpf = str(exc).split("cpf")[1].split(")")[0].strip()
        return JSONResponse(
            status_code=303,
            content={"detail": f"Já existe um atleta cadastrado com o cpf: {cpf}"},
            headers={"Location": "/atletas"}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro de integridade do banco de dados"},
    )
