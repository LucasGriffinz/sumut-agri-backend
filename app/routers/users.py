from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole
from app.schemas import UserRegister, UserLogin, UserOut, ResetPasswordInput
# 1. IMPORT DARI SECURITY DAN DEPENDENCIES YANG SUDAH DIBUAT
from app.security import hash_password, verify_password, create_access_token
from app.dependencies import require_admin, get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])

# ==================== 1. REGISTRASI PUBLIK (PETANI) ====================
@router.post("/register", response_model=UserOut)
def register(data: UserRegister, db: Session = Depends(get_db)):
    email_clean = data.email.lower()
    
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
        
    if data.no_hp:
        hp_exist = db.query(User).filter(User.no_hp == data.no_hp).first()
        if hp_exist:
            raise HTTPException(status_code=400, detail="No HP sudah digunakan")
            
    # Buat objek user terlebih dahulu
    user = User(
        nama_lengkap=data.nama_lengkap,
        email=email_clean,
        password_hash=hash_password(data.password),
        no_hp=data.no_hp,
        alamat=data.alamat,
        kabupaten_kota=data.kabupaten_kota,
    )
    
    # PERBAIKAN PENGUNCIAN MUTLAK:
    # Paksa role objek ini menjadi PETANI secara eksplisit tepat sebelum disimpan
    # Ini akan menghapus nilai role apapun yang dikirim nakal/tidak sengaja oleh aplikasi mobile
    user.role = UserRole.PETANI  
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ==================== 2. ENDPOINT LOGIN (MENGHASILKAN JWT TOKEN) ====================
@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    # Pencarian disamakan ke lowercase agar case-insensitive saat login
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    # BUAT TOKEN JWT DI SINI
    # Simpan email, id, dan role ke dalam token payload
    access_token = create_access_token(
        data={"sub": user.email, "id": user.id, "role": user.role}
    )
    
    # PERBAIKAN: Mengembalikan token beserta metadata profil user untuk kemudahan UI Android & Web Admin
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "nama_lengkap": user.nama_lengkap,
            "email": user.email,
            "role": user.role,
            "kabupaten_kota": user.kabupaten_kota
        }
    }

# ==================== 3. GET ALL USERS (DIKUNCI: HANYA ADMIN YANG BISA LIHAT) ====================
@router.get("/", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db), current_admin: User = Depends(require_admin)):
    return db.query(User).all()

# ==================== 4. CEK PROFIL SENDIRI (OPSIONAL - SANGAT BERGUNA UNTUK ANDROID/WEB) ====================
@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

# ==================== 5. ENDPOINT RESET PASSWORD HIERARKIS (TAMBAHAN BARU) ====================
@router.post("/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    payload: ResetPasswordInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # a. Cari user target di database PostgreSQL
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")
    
    # b. Validasi Aturan Hierarki Otoritas Akses
    if current_user.role == UserRole.PETUGAS:
        # Petugas HANYA boleh mereset password PETANI
        if target_user.role != UserRole.PETANI:
            raise HTTPException(
                status_code=403, 
                detail="Akses ditolak. Petugas hanya diizinkan mereset password Petani."
            )
        # Petugas hanya boleh mereset petani di wilayah operasionalnya sendiri
        if current_user.kabupaten_kota != target_user.kabupaten_kota:
            raise HTTPException(
                status_code=403, 
                detail="Akses ditolak. Petani berada di luar wilayah operasional Anda."
            )
            
    elif current_user.role == UserRole.ADMIN:
        # Admin berhak mutlak mereset siapa saja (ADMIN, PETUGAS, PETANI)
        pass
    else:
        # Mencegah role PETANI melakukan manipulasi HTTP Request via tools luar
        raise HTTPException(status_code=403, detail="Tindakan ilegal. Anda tidak memiliki otoritas.")
    
    # c. Enkripsi password baru dan simpan kembali ke database lokal/cloud Railway
    target_user.password_hash = hash_password(payload.new_password)
    db.commit()
    
    return {
        "status": "success", 
        "message": f"Password untuk {target_user.nama_lengkap} berhasil diperbarui."
    }