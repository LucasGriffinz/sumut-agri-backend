from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole
from app.schemas import UserRegister, UserOut
from passlib.context import CryptContext

router = APIRouter(prefix="/api/admin", tags=["Admin"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/users", response_model=UserOut)
def create_user_by_admin(
    data: UserRegister,
    role: UserRole = Query(..., description="Role: admin, petugas, petani"),
    db: Session = Depends(get_db)
):
    # Cek apakah email sudah terdaftar
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    # Validasi role
    if role not in [UserRole.ADMIN, UserRole.PETUGAS, UserRole.PETANI]:
        raise HTTPException(status_code=400, detail="Role tidak valid")

    # Buat user dengan password ter-hash
    user = User(
        nama_lengkap=data.nama_lengkap,
        email=data.email,
        password_hash=pwd_context.hash(data.password),
        role=role,
        no_hp=data.no_hp,
        alamat=data.alamat,
        kabupaten_kota=data.kabupaten_kota,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user