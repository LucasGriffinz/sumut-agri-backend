from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models import HargaHarian, Komoditas, User
from app.schemas import HargaHarianCreate, HargaHarianOut
# Import satpam pengaman token & role
from app.dependencies import get_current_user, require_petugas

router = APIRouter(prefix="/api/harga", tags=["Harga Harian"])

# ==================== 1. AMBIL SEMUA DATA HARGA HARIAN ====================
# Semua user yang sudah login (Admin, Petugas, Petani) boleh melihat riwayat harga
@router.get("/", response_model=list[HargaHarianOut])
def get_all_harga(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Digembok: minimal harus login
):
    return db.query(HargaHarian).order_by(HargaHarian.tanggal.desc()).all()


# ==================== 2. INPUT DATA HARGA HARIAN (KHUSUS ADMIN/PETUGAS) ====================
# Hanya Petugas atau Admin yang bisa menambah/memperbarui harga komoditas pasar
@router.post("/", response_model=HargaHarianOut, status_code=status.HTTP_201_CREATED)
def create_harga(
    data: HargaHarianCreate, 
    db: Session = Depends(get_db),
    current_staff: User = Depends(require_petugas) # DIKUNCI: Hanya Petugas/Admin
):
    # Validasi memastikan komoditas terdaftar di DB
    komoditas = db.query(Komoditas).filter(Komoditas.id == data.id_komoditas).first()
    if not komoditas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Komoditas tidak ditemukan"
        )
    
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