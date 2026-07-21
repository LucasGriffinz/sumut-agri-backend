from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Kecamatan, Desa
from app.schemas import KecamatanOut, DesaOut

router = APIRouter(prefix="/api/wilayah", tags=["Wilayah Deli Serdang"])

# 1. GET Semua Kecamatan di Deli Serdang
@router.get("/kecamatan", response_model=list[KecamatanOut])
def get_all_kecamatan(db: Session = Depends(get_db)):
    return db.query(Kecamatan).order_by(Kecamatan.nama_kecamatan.asc()).all()

# 2. GET Desa berdasarkan ID Kecamatan yang dipilih
@router.get("/desa/{id_kecamatan}", response_model=list[DesaOut])
def get_desa_by_kecamatan(id_kecamatan: int, db: Session = Depends(get_db)):
    return db.query(Desa).filter(Desa.id_kecamatan == id_kecamatan).order_by(Desa.nama_desa.asc()).all()