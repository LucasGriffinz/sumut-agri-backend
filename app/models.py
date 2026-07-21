from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime,
    ForeignKey, Enum as SQLEnum, Text, func
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import date

# ================== ENUMS ==================
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    PETUGAS = "PETUGAS"
    PETANI = "PETANI"

class StatusDistribusi(str, enum.Enum):
    DIKIRIM = "dikirim"
    DALAM_PERJALANAN = "dalam_perjalanan"
    SAMPAI = "sampai"

# ================== ENTITAS WILAYAH DELI SERDANG ==================

class Kecamatan(Base):
    __tablename__ = "kecamatan"

    id = Column(Integer, primary_key=True, index=True)
    nama_kecamatan = Column(String(100), unique=True, nullable=False)

    # Relasi ke Desa
    desa = relationship("Desa", back_populates="kecamatan", cascade="all, delete-orphan")
    produksi = relationship("Produksi", back_populates="kecamatan")

class Desa(Base):
    __tablename__ = "desa"

    id = Column(Integer, primary_key=True, index=True)
    id_kecamatan = Column(Integer, ForeignKey("kecamatan.id"), nullable=False)
    nama_desa = Column(String(100), nullable=False)

    # Relasi
    kecamatan = relationship("Kecamatan", back_populates="desa")
    produksi = relationship("Produksi", back_populates="desa")

# ================== ENTITAS UTAMA ==================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nama_lengkap = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  
    role = Column(SQLEnum(UserRole, name="user_role_enum"), default=UserRole.PETANI, nullable=False)
    no_hp = Column(String(15), unique=True, nullable=True)
    alamat = Column(Text, nullable=True)
    kabupaten_kota = Column(String(50), nullable=True)  
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    produksi = relationship("Produksi", back_populates="petani")
    distribusi = relationship("Distribusi", back_populates="petugas_pencatat")

class Komoditas(Base):
    __tablename__ = "komoditas"

    id = Column(Integer, primary_key=True, index=True)
    nama_komoditas = Column(String(100), unique=True, nullable=False)
    satuan = Column(String(20), nullable=False, default="kg")  
    deskripsi = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    produksi = relationship("Produksi", back_populates="komoditas")
    harga_harian = relationship("HargaHarian", back_populates="komoditas")
    distribusi = relationship("Distribusi", back_populates="komoditas")

class Produksi(Base):
    __tablename__ = "produksi"

    id = Column(Integer, primary_key=True, index=True)
    id_petani = Column(Integer, ForeignKey("users.id"), nullable=False)
    id_komoditas = Column(Integer, ForeignKey("komoditas.id"), nullable=False)
    
    # 🌟 BARU: Relasi ke Master Wilayah Deli Serdang
    id_kecamatan = Column(Integer, ForeignKey("kecamatan.id"), nullable=True)
    id_desa = Column(Integer, ForeignKey("desa.id"), nullable=True)
    
    jumlah_panen = Column(Float, nullable=False)  
    luas_lahan = Column(Float, nullable=True)  
    tanggal_panen = Column(Date, default=date.today)
    lokasi = Column(String(150), nullable=True)  # Teks penjelas (misal: "Desa X, Kec Y")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    status = Column(String(20), default="pending")  

    petani = relationship("User", back_populates="produksi")
    komoditas = relationship("Komoditas", back_populates="produksi")
    kecamatan = relationship("Kecamatan", back_populates="produksi")
    desa = relationship("Desa", back_populates="produksi")

class HargaHarian(Base):
    __tablename__ = "harga_harian"

    id = Column(Integer, primary_key=True, index=True)
    id_komoditas = Column(Integer, ForeignKey("komoditas.id"), nullable=False)
    harga_per_satuan = Column(Float, nullable=False)  
    tanggal = Column(Date, default=date.today)
    pasar_sumber = Column(String(100), nullable=True)  
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    komoditas = relationship("Komoditas", back_populates="harga_harian")

class Distribusi(Base):
    __tablename__ = "distribusi"

    id = Column(Integer, primary_key=True, index=True)
    id_komoditas = Column(Integer, ForeignKey("komoditas.id"), nullable=False)
    id_petugas = Column(Integer, ForeignKey("users.id"), nullable=False)  
    jumlah = Column(Float, nullable=False)
    asal = Column(String(100), nullable=False)  
    tujuan = Column(String(100), nullable=False)  
    tanggal_kirim = Column(Date, default=date.today)
    status = Column(SQLEnum(StatusDistribusi, name="status_distribusi_enum"), default=StatusDistribusi.DIKIRIM)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    komoditas = relationship("Komoditas", back_populates="distribusi")
    petugas_pencatat = relationship("User", back_populates="distribusi")