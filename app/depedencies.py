import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole

# 1. Tentukan ke mana FastAPI harus mencari token.
# Di dalam app/dependencies.py, sesuaikan baris ini:
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/login")

# Ambil konfigurasi JWT dari security (pastikan sama dengan di security.py)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "SUPER_SECRET_KEY_SUMUT_AGRI_2026")
ALGORITHM = "HS256"

# ==================== FUNGSI PROTEKSI 1: VERIFIKASI TOKEN ====================
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Fungsi ini mengekstrak token JWT, mendekripsinya, 
    dan memastikan user tersebut benar-benar terdaftar di database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesi Anda telah berakhir atau token tidak valid. Silakan login kembali.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Dekripsi token JWT menggunakan SECRET_KEY
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")  # Kita menggunakan email sebagai sub saat login
        
        if email is None:
            raise credentials_exception
            
    except jwt.PyJWTError:
        # Jika token expired, corrupt, atau dimanipulasi, langsung lempar error
        raise credentials_exception

    # Cari user di database berdasarkan email dari token
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user  # Mengembalikan objek User yang sedang login


# ==================== FUNGSI PROTEKSI 2: RBAC UNTUK ADMIN ====================
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Hanya meloloskan user yang memiliki role ADMIN.
    Cocok untuk website kendali pusat.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses Ditolak! Endpoint ini hanya khusus untuk Admin Utama."
        )
    return current_user


# ==================== FUNGSI PROTEKSI 3: RBAC UNTUK PETUGAS ====================
def require_petugas(current_user: User = Depends(get_current_user)) -> User:
    """
    Meloloskan user yang memiliki role PETUGAS atau ADMIN (karena Admin punya hak tertinggi).
    Cocok untuk verifikasi panen dan input harga pasar.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.PETUGAS]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses Ditolak! Hanya Petugas Lapangan atau Admin yang diizinkan."
        )
    return current_user