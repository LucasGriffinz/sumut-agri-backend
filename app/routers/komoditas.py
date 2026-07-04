from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Komoditas
from app.schemas import KomoditasCreate, KomoditasOut

router = APIRouter(prefix="/api/komoditas", tags=["Komoditas"])

@router.get("/", response_model=list[KomoditasOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(Komoditas).all()

@router.post("/", response_model=KomoditasOut, status_code=201)
def create(data: KomoditasCreate, db: Session = Depends(get_db)):
    existing = db.query(Komoditas).filter(Komoditas.nama_komoditas == data.nama_komoditas).first()
    if existing:
        raise HTTPException(status_code=400, detail="Komoditas sudah ada")
    komoditas = Komoditas(**data.dict())
    db.add(komoditas)
    db.commit()
    db.refresh(komoditas)
    return komoditas