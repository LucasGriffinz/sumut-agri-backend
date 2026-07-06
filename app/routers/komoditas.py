from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Komoditas, User
from app.schemas import KomoditasCreate, KomoditasOut
# Import fungsi proteksi keamanan token dan role
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/komoditas", tags=["Komoditas"])

# ==================== 1. AMBIL SEMUA JENIS KOMODITAS ====================
# Semua user yang sudah login (Admin, Petugas, Petani) boleh melihat daftar komoditas
@router.get("/", response_model=list[KomoditasOut])
def get_all_komoditas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Digembok: minimal harus login
):
    return db.query(Komoditas).all()


# ==================== 2. TAMBAH KOMODITAS BARU (KHUSUS ADMIN) ====================
# Hanya Admin Utama yang memiliki wewenang menambah jenis master data komoditas baru
@router.post("/", response_model=KomoditasOut, status_code=status.HTTP_201_CREATED)
def create_komoditas(
    data: KomoditasCreate, 
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin) # DIKUNCI KETAT: Hanya Admin
):
    # Validasi memastikan nama komoditas belum ada di DB
    existing = db.query(Komoditas).filter(Komoditas.nama_komoditas == data.nama_komoditas).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Komoditas sudah ada"
        )
    
    # Pydantic v2 kompatibilitas (.model_dump() menggantikan .dict())
    komoditas = Komoditas(**data.model_dump())
    
    db.add(komoditas)
    db.commit()
    db.refresh(komoditas)
    return komoditas