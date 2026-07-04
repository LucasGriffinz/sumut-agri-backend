from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models import HargaHarian, Komoditas
from app.schemas import HargaHarianCreate, HargaHarianOut

router = APIRouter(prefix="/api/harga", tags=["Harga Harian"])

@router.get("/", response_model=list[HargaHarianOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(HargaHarian).order_by(HargaHarian.tanggal.desc()).all()

@router.post("/", response_model=HargaHarianOut, status_code=201)
def create(data: HargaHarianCreate, db: Session = Depends(get_db)):
    # Validasi komoditas ada
    komoditas = db.query(Komoditas).filter(Komoditas.id == data.id_komoditas).first()
    if not komoditas:
        raise HTTPException(status_code=400, detail="Komoditas tidak ditemukan")
    harga = HargaHarian(
        id_komoditas=data.id_komoditas,
        harga_per_satuan=data.harga_per_satuan,
        tanggal=data.tanggal or date.today(),
        pasar_sumber=data.pasar_sumber
    )
    db.add(harga)
    db.commit()
    db.refresh(harga)
    return harga