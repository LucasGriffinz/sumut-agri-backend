from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Distribusi, User, StatusDistribusi
from app.schemas import DistribusiCreate, DistribusiUpdateStatus, DistribusiOut
# Import fungsi proteksi token & role
from app.dependencies import get_current_user, require_petugas

router = APIRouter(prefix="/api/distribusi", tags=["Distribusi"])

# ==================== 1. AMBIL SEMUA DATA DISTRIBUSI ====================
# Semua user yang sudah login (Admin, Petugas, Petani) boleh melihat data ini
@router.get("/", response_model=list[DistribusiOut])
def get_all_distribusi(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Digunakan joinedload (jika di models.py sudah ada relationship) atau query standar
    # Mengurutkan dari ID terbesar/terbaru agar status kiriman terbaru muncul di atas
    return db.query(Distribusi).order_by(Distribusi.id.desc()).all()


# ==================== 2. CATAT DISTRIBUSI BARU (KHUSUS PETUGAS) ====================
# Hanya Petugas Lapangan atau Admin yang bisa menginput distribusi komoditas
@router.post("/input", response_model=DistribusiOut, status_code=status.HTTP_201_CREATED)
def input_distribusi(
    data: DistribusiCreate, 
    db: Session = Depends(get_db), 
    current_staff: User = Depends(require_petugas)
):
    # ID petugas penginput otomatis diambil dari token JWT yang sedang aktif
    new_distribusi = Distribusi(
        id_komoditas=data.id_komoditas,
        id_petugas=current_staff.id,  # Mengunci pencatat ke ID petugas aktif
        jumlah=data.jumlah,
        asal=data.asal,
        tujuan=data.tujuan,
        tanggal_kirim=data.tanggal_kirim,
        status=StatusDistribusi.DIKIRIM if hasattr(StatusDistribusi, 'DIKIRIM') else data.status
    )
    
    db.add(new_distribusi)
    db.commit()
    db.refresh(new_distribusi)
    return new_distribusi


# ==================== 3. UPDATE STATUS DISTRIBUSI (KHUSUS PETUGAS) ====================
# Digunakan untuk mengubah status (misal: 'dikirim' menjadi 'transit' atau 'selesai')
@router.patch("/update-status/{distribusi_id}", response_model=DistribusiOut)
def update_status_distribusi(
    distribusi_id: int,
    data: DistribusiUpdateStatus,
    db: Session = Depends(get_db),
    current_staff: User = Depends(require_petugas)
):
    # Cari data distribusi berdasarkan ID
    distribusi = db.query(Distribusi).filter(Distribusi.id == distribusi_id).first()
    
    if not distribusi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Data distribusi tidak ditemukan"
        )
    
    # Update status baru
    distribusi.status = data.status
    
    db.commit()
    db.refresh(distribusi)
    
    # 🌟 PERBAIKAN: Menghapus minus '-' agar objek mengembalikan data distribusi yang valid
    return distribusi