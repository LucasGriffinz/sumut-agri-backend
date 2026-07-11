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

# 🌟 PERBAIKAN UTAMA: Schema Response Login yang Kokoh & Sesuai Best Practice REST API
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut  # Menjamin semua field di UserOut (termasuk ID) ikut dikirim ke Android


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
    id: int  # Field ini sudah benar ada di sini
    nama_lengkap: str
    email: str
    role: UserRole
    no_hp: Optional[str] = None
    alamat: Optional[str] = None
    kabupaten_kota: Optional[str] = None
    # PERBAIKAN: Diubah menjadi Optional agar menerima nilai null dari PostgreSQL Railway
    created_at: Optional[datetime] = None

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
    # PERBAIKAN: Antisipasi null pada metadata komoditas hulu
    created_at: Optional[datetime] = None

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
    # PERBAIKAN: Antisipasi null pada pencatatan log harga
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== 5. PRODUKSI SCHEMAS ====================
class ProduksiCreate(BaseModel):
    id_komoditas: int
    jumlah_panen: float
    luas_lahan: Optional[float] = None
    tanggal_panen: Optional[date] = None
    lokasi: Optional[str] = None

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
    # PERBAIKAN: Antisipasi null pada panen masuk
    created_at: Optional[datetime] = None

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
    # PERBAIKAN: Antisipasi data null pada log distribusi logistik pangan
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ResetPasswordInput(BaseModel):
    new_password: str

    class Config:
        from_attributes = True