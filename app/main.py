from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate

from app.database.connection import get_db, Base, engine
from app.models.atleta import Atleta
from app.schemas.atleta import AtletaResponse, AtletaCreate, AtletaUpdate
from app.exceptions import IntegrityException, integrity_exception_handler

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Workout API", version="1.0.0")
app.add_exception_handler(IntegrityError, integrity_exception_handler)

@app.get("/atletas", response_model=Page[AtletaResponse])
def listar_atletas(
    db: Session = Depends(get_db),
    nome: str = Query(None, description="Filtrar por nome"),
    cpf: str = Query(None, description="Filtrar por CPF"),
    limit: int = Query(50, ge=1, le=100, description="Limite de resultados por página"),
    offset: int = Query(0, ge=0, description="Deslocamento na paginação")
):
    query = db.query(Atleta)
    
    if nome:
        query = query.filter(Atleta.nome.ilike(f"%{nome}%"))
    if cpf:
        query = query.filter(Atleta.cpf == cpf)
    
    return paginate(query)

@app.get("/atletas/{atleta_id}", response_model=AtletaResponse)
def obter_atleta(atleta_id: int, db: Session = Depends(get_db)):
    atleta = db.query(Atleta).filter(Atleta.id == atleta_id).first()
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    return atleta

@app.post("/atletas", response_model=AtletaResponse, status_code=201)
def criar_atleta(atleta: AtletaCreate, db: Session = Depends(get_db)):
    try:
        db_atleta = Atleta(**atleta.dict())
        db.add(db_atleta)
        db.commit()
        db.refresh(db_atleta)
        return db_atleta
    except IntegrityError as e:
        if "cpf" in str(e).lower():
            raise IntegrityException(detail=f"Já existe um atleta cadastrado com o cpf: {atleta.cpf}")
        raise

@app.put("/atletas/{atleta_id}", response_model=AtletaResponse)
def atualizar_atleta(atleta_id: int, atleta: AtletaUpdate, db: Session = Depends(get_db)):
    db_atleta = db.query(Atleta).filter(Atleta.id == atleta_id).first()
    if not db_atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    for key, value in atleta.dict(exclude_unset=True).items():
        setattr(db_atleta, key, value)
    
    try:
        db.commit()
        db.refresh(db_atleta)
        return db_atleta
    except IntegrityError as e:
        if "cpf" in str(e).lower():
            raise IntegrityException(detail=f"Já existe um atleta cadastrado com o cpf: {atleta.cpf}")
        raise

@app.delete("/atletas/{atleta_id}", status_code=204)
def deletar_atleta(atleta_id: int, db: Session = Depends(get_db)):
    atleta = db.query(Atleta).filter(Atleta.id == atleta_id).first()
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    db.delete(atleta)
    db.commit()

add_pagination(app)
