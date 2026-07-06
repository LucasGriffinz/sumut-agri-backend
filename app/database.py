import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Alamat PostgreSQL lokal Anda (Sesuaikan password 'admin123' jika berbeda saat install)
LOCAL_DATABASE_URL = "postgresql://postgres:1234@localhost:5432/sumut_agri_db"

# 2. Ambil URL database dari environment variable (untuk Railway). 
# Jika tidak ada, otomatis pakai LOCAL_DATABASE_URL (untuk laptop)
DATABASE_URL = os.getenv("DATABASE_URL", LOCAL_DATABASE_URL)

# 3. FIX UNTUK RAILWAY: Ubah postgres:// menjadi postgresql:// jika terdeteksi dari cloud
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 4. Konfigurasi Engine berdasarkan jenis Database
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}  # Hanya jika suatu saat Anda balik pakai SQLite
    )
else:
    # Digunakan untuk PostgreSQL lokal maupun PostgreSQL Railway
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()