from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models import Produksi, User, Komoditas
from app.schemas import ProduksiCreate, ProduksiOut
from typing import Optional

router = APIRouter(prefix="/api/produksi", tags=["Produksi"])

@router.get("/", response_model=list[ProduksiOut])
def get_all(id_petani: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Produksi)
    if id_petani is not None:
        query = query.filter(Produksi.id_petani == id_petani)
    return query.order_by(Produksi.tanggal_panen.desc()).all()

@router.post("/", response_model=ProduksiOut, status_code=201)
def create(data: ProduksiCreate, db: Session = Depends(get_db)):
    """Input oleh petani"""
    # Validasi petani ada
    petani = db.query(User).filter(User.id == data.id_petani, User.role == "petani").first()
    if not petani:
        raise HTTPException(status_code=400, detail="Petani tidak valid")
    # Validasi komoditas
    komoditas = db.query(Komoditas).filter(Komoditas.id == data.id_komoditas).first()
    if not komoditas:
        raise HTTPException(status_code=400, detail="Komoditas tidak ditemukan")
    produksi = Produksi(
        id_petani=data.id_petani,
        id_komoditas=data.id_komoditas,
        jumlah_panen=data.jumlah_panen,
        luas_lahan=data.luas_lahan,
        tanggal_panen=data.tanggal_panen or date.today(),
        lokasi=data.lokasi
    )
    db.add(produksi)
    db.commit()
    db.refresh(produksi)
    return produksi

@router.patch("/{produksi_id}/verifikasi", response_model=ProduksiOut)
def verifikasi_produksi(produksi_id: int, db: Session = Depends(get_db)):
    produksi = db.query(Produksi).filter(Produksi.id == produksi_id).first()
    if not produksi:
        raise HTTPException(status_code=404, detail="Produksi tidak ditemukan")
    if produksi.status != "pending":
        raise HTTPException(status_code=400, detail="Hanya produksi pending yang bisa diverifikasi")
    produksi.status = "disetujui"
    db.commit()
    db.refresh(produksi)
    return produksi

@router.patch("/{produksi_id}/tolak", response_model=ProduksiOut)
def tolak_produksi(produksi_id: int, db: Session = Depends(get_db)):
    produksi = db.query(Produksi).filter(Produksi.id == produksi_id).first()
    if not produksi:
        raise HTTPException(status_code=404, detail="Produksi tidak ditemukan")
    if produksi.status != "pending":
        raise HTTPException(status_code=400, detail="Hanya produksi pending yang bisa ditolak")
    produksi.status = "ditolak"
    db.commit()
    db.refresh(produksi)
    return produksi