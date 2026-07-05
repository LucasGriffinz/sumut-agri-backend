import os
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext

# Konfigurasi Hashing Password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Konfigurasi JWT (Ambil SECRET_KEY dari Railway, jangan di-hardcode)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "SUPER_SECRET_KEY_SUMUT_AGRI_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token hangus dalam 1 jam

def hash_password(password: str) -> str:
    """Mengubah password teks biasa menjadi hash acak untuk disimpan di DB"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Mengecek apakah password login cocok dengan hash di DB"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Membuat token JWT dengan data user dan waktu kedaluwarsa"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt