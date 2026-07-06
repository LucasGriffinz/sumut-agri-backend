from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models import Produksi, User, Komoditas, UserRole
from app.schemas import ProduksiCreate, ProduksiOut, ProduksiVerifikasi
from typing import Optional
# Import satpam token & role
from app.dependencies import get_current_user, require_petugas

router = APIRouter(prefix="/api/produksi", tags=["Produksi"])

# ==================== 1. AMBIL DATA PRODUKSI (BERDASARKAN ROLE) ====================
@router.get("/", response_model=list[ProduksiOut])
def get_all_produksi(
    id_petani: Optional[int] = None, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Produksi)
    
    # JIKA YANG LOGIN PETANI: Paksa hanya melihat data miliknya sendiri
    if current_user.role == UserRole.PETANI:
        query = query.filter(Produksi.id_petani == current_user.id)
    else:
        # JIKA ADMIN/PETUGAS: Bebas melihat semua, atau filter opsional lewat query string
        if id_petani is not None:
            query = query.filter(Produksi.id_petani == id_petani)
            
    return query.order_by(Produksi.tanggal_panen.desc()).all()


# ==================== 2. INPUT DATA PRODUKSI (KHUSUS PETANI VIA ANDROID) ====================
@router.post("/", response_model=ProduksiOut, status_code=status.HTTP_201_CREATED)
def create_produksi(
    data: ProduksiCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Input oleh petani mandiri"""
    # Pastikan yang menginput benar-benar memiliki role PETANI
    if current_user.role != UserRole.PETANI:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya akun Petani yang dapat mencatat hasil produksi panen."
        )

    # Validasi komoditas terdaftar di DB
    komoditas = db.query(Komoditas).filter(Komoditas.id == data.id_komoditas).first()
    if not komoditas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Komoditas tidak ditemukan"
        )
        
    new_produksi = Produksi(
        id_petani=current_user.id,  # Mengunci otomatis ke ID petani yang sedang login
        id_komoditas=data.id_komoditas,
        jumlah_panen=data.jumlah_panen,
        luas_lahan=data.luas_lahan,
        tanggal_panen=data.tanggal_panen or date.today(),
        lokasi=data.lokasi,
        status="pending"  # Default awal di-set oleh sistem
    )
    
    db.add(new_produksi)
    db.commit()
    db.refresh(new_produksi)
    return new_produksi


# ==================== 3. VERIFIKASI PRODUKSI (KHUSUS ADMIN/PETUGAS VIA WEB) ====================
@router.patch("/{produksi_id}/verifikasi", response_model=ProduksiOut)
def verifikasi_produksi(
    produksi_id: int, 
    db: Session = Depends(get_db),
    current_staff: User = Depends(require_petugas) # DIKUNCI: Hanya Petugas/Admin
):
    produksi = db.query(Produksi).filter(Produksi.id == produksi_id).first()
    if not produksi:
        raise HTTPException(status_code=404, detail="Data produksi tidak ditemukan")
        
    if produksi.status != "pending":
        raise HTTPException(status_code=400, detail="Hanya data produksi dengan status 'pending' yang bisa diverifikasi")
        
    produksi.status = "disetujui"
    db.commit()
    db.refresh(produksi)
    return produksi


# ==================== 4. TOLAK AJUAN PRODUKSI (KHUSUS ADMIN/PETUGAS VIA WEB) ====================
@router.patch("/{produksi_id}/tolak", response_model=ProduksiOut)
def tolak_produksi(
    produksi_id: int, 
    db: Session = Depends(get_db),
    current_staff: User = Depends(require_petugas) # DIKUNCI: Hanya Petugas/Admin
):
    produksi = db.query(Produksi).filter(Produksi.id == produksi_id).first()
    if not produksi:
        raise HTTPException(status_code=404, detail="Data produksi tidak ditemukan")
        
    if produksi.status != "pending":
        raise HTTPException(status_code=400, detail="Hanya data produksi dengan status 'pending' yang bisa ditolak")
        
    produksi.status = "ditolak"
    db.commit()
    db.refresh(produksi)
    return produksi