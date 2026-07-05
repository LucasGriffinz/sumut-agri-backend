from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole
from app.schemas import UserRegister, UserLogin, UserOut
# 1. IMPORT DARI SECURITY DAN DEPENDENCIES YANG SUDAH DIBUAT
from app.security import hash_password, verify_password, create_access_token
from app.dependencies import require_admin, get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])

# ==================== 1. REGISTRASI PUBLIK (PETANI) ====================
@router.post("/register", response_model=UserOut)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    if data.no_hp:
        hp_exist = db.query(User).filter(User.no_hp == data.no_hp).first()
        if hp_exist:
            raise HTTPException(status_code=400, detail="No HP sudah digunakan")
            
    user = User(
        nama_lengkap=data.nama_lengkap,
        email=data.email,
        password_hash=hash_password(data.password), # Menggunakan fungsi dari security.py
        role=UserRole.PETANI,   # Registrasi publik otomatis sebagai petani menggunakan Enum
        no_hp=data.no_hp,
        alamat=data.alamat,
        kabupaten_kota=data.kabupaten_kota,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ==================== 2. ENDPOINT LOGIN (MENGHASILKAN JWT TOKEN) ====================
# Response model dilepas dari UserOut karena kita ingin mengembalikan token string, bukan data user mentah
@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    # BUAT TOKEN JWT DI SINI
    # Simpan email, id, dan role ke dalam token payload
    access_token = create_access_token(
        data={"sub": user.email, "id": user.id, "role": user.role}
    )
    
    # Android & Web Admin akan menyimpan token ini
    return {"access_token": access_token, "token_type": "bearer"}

# ==================== 3. GET ALL USERS (DIKUNCI: HANYA ADMIN YANG BISA LIHAT) ====================
# Sebelumnya endpoint ini terbuka untuk umum, sekarang kita kunci demi keamanan data pengguna
@router.get("/", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db), current_admin: User = Depends(require_admin)):
    return db.query(User).all()

# ==================== 4. CEK PROFIL SENDIRI (OPSIONAL - SANGAT BERGUNA UNTUK ANDROID/WEB) ====================
# Endpoint untuk melihat data profil user yang sedang login saat ini
@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user