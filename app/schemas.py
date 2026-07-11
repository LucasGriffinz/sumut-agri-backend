from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from app.models import UserRole, StatusDistribusi

# ===== User =====
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
    kabupaten_kota: Optional[str] = None

    class Config:
        from_attributes = True
        
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut  # Sekarang dijamin aman dan terdefinisi!

# ===== Komoditas =====
class KomoditasCreate(BaseModel):
    nama_komoditas: str
    satuan: str = "kg"
    deskripsi: Optional[str] = None

class KomoditasOut(BaseModel):
    id: int
    nama_komoditas: str
    satuan: str
    deskripsi: Optional[str] = None

    class Config:
        from_attributes = True

# ===== Harga Harian =====
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

    class Config:
        from_attributes = True

# ===== Produksi =====
class ProduksiCreate(BaseModel):
    id_petani: int          # nanti setelah ada auth bisa diambil dari token
    id_komoditas: int
    jumlah_panen: float
    luas_lahan: Optional[float] = None
    tanggal_panen: Optional[date] = None
    lokasi: Optional[str] = None

class ProduksiOut(BaseModel):
    id: int
    id_petani: int
    id_komoditas: int
    jumlah_panen: float
    luas_lahan: Optional[float] = None
    tanggal_panen: date
    lokasi: Optional[str] = None
    status: str              # <-- tambahkan

    class Config:
        from_attributes = True

class HargaHarianCreate(BaseModel):
    id_komoditas: int
    harga_per_satuan: float
    tanggal: Optional[date] = None
    pasar_sumber: Optional[str] = None
