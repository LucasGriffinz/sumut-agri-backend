from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from app.models import UserRole, StatusDistribusi

# ==================== 1. TOKENS (Untuk Dokumentasi Swagger/Auth) ====================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


# ==================== 2. USER SCHEMAS ====================
class UserRegister(BaseModel):
    nama_lengkap: str
    email: EmailStr
    password: str
    no_hp: Optional[str] = None
    alamat: Optional[str] = None
    kabupaten_kota: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    nama_lengkap: str
    email: str
    role: UserRole
    no_hp: Optional[str] = None
    alamat: Optional[str] = None
    kabupaten_kota: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 3. KOMODITAS SCHEMAS ====================
class KomoditasCreate(BaseModel):
    nama_komoditas: str
    satuan: str = "kg"
    deskripsi: Optional[str] = None

class KomoditasOut(BaseModel):
    id: int
    nama_komoditas: str
    satuan: str
    deskripsi: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 4. HARGA HARIAN SCHEMAS ====================
class HargaHarianCreate(BaseModel):
    id_komoditas: int
    harga_per_satuan: float
    tanggal: Optional[date] = None
    pasar_sumber: Optional[str] = None

class HargaHarianOut(BaseModel):
    id: int
    id_komoditas: int
    harga_per_satuan: float
    tanggal: date
    pasar_sumber: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 5. PRODUKSI SCHEMAS ====================
class ProduksiCreate(BaseModel):
    id_komoditas: int
    jumlah_panen: float
    luas_lahan: Optional[float] = None
    tanggal_panen: Optional[date] = None
    lokasi: Optional[str] = None

# Skema khusus Petugas saat menyetujui/menolak ajuan panen petani
class ProduksiVerifikasi(BaseModel):
    status: str  # 'disetujui' atau 'ditolak'

class ProduksiOut(BaseModel):
    id: int
    id_petani: int
    id_komoditas: int
    jumlah_panen: float
    luas_lahan: Optional[float] = None
    tanggal_panen: date
    lokasi: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 6. DISTRIBUSI SCHEMAS (TAMBAHAN BARU) ====================
class DistribusiCreate(BaseModel):
    id_komoditas: int
    jumlah: float
    asal: str
    tujuan: str
    tanggal_kirim: Optional[date] = None

class DistribusiUpdateStatus(BaseModel):
    status: StatusDistribusi

class DistribusiOut(BaseModel):
    id: int
    id_komoditas: int
    id_petugas: int
    jumlah: float
    asal: str
    tujuan: str
    tanggal_kirim: date
    status: StatusDistribusi
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True