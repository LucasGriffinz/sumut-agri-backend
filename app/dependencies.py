import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole

# 1. Pastikan tokenUrl mengarah tepat ke endpoint login Anda yang mengembalikan token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/login", auto_error=False)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "SUPER_SECRET_KEY_SUMUT_AGRI_2026")
ALGORITHM = "HS256"

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesi Anda telah berakhir atau token tidak valid. Silakan login kembali.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Jika token sama sekali tidak dikirim oleh frontend
    if not token:
        print("[AUTH ERROR]: Token tidak ditemukan di Header HTTP!")
        raise credentials_exception
        
    try:
        # Dekripsi token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            print("[AUTH ERROR]: Payload sub (email) kosong!")
            raise credentials_exception
            
    except jwt.PyJWTError as e:
        print(f"[AUTH ERROR]: Gagal dekripsi JWT -> {str(e)}")
        raise credentials_exception

    # Cari user di database
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        print(f"[AUTH ERROR]: User dengan email {email} tidak terdaftar di DB!")
        raise credentials_exception
        
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    # Menggunakan perbandingan string .value agar toleran terhadap objek Enum vs String DB
    current_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    
    print(f"[RBAC CHECK]: User {current_user.email} memiliki role {current_role}")
    
    if current_role.upper() != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses Ditolak! Endpoint ini hanya khusus untuk Admin Utama."
        )
    return current_user


def require_petugas(current_user: User = Depends(get_current_user)) -> User:
    current_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    
    if current_role.upper() not in ["ADMIN", "PETUGAS"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses Ditolak! Hanya Petugas Lapangan atau Admin yang diizinkan."
        )
    return current_user