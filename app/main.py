from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
# Import models dipastikan tetap ada agar SQLAlchemy tahu tabel apa saja yang harus dibuat
from app.models import User, Komoditas, Produksi, HargaHarian, Distribusi
from app.routers import users, komoditas, harga, produksi, admin, distribusi

# Menggunakan lifespan untuk menggantikan @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Logika saat aplikasi baru dinyalakan (Startup)
    Base.metadata.create_all(bind=engine)
    yield
    # Logika saat aplikasi dimatikan (Shutdown) - jika ada bisa ditaruh di sini

app = FastAPI(
    title="Sumut Agri API",
    description="Sistem Pemantauan Komoditas Pertanian Sumatera Utara",
    version="1.0.0",
    lifespan=lifespan  # Daftarkan lifespan di sini
)

# CORS (Sangat cocok untuk dev, sesuaikan domainnya saat production nanti)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrasi Router
app.include_router(users.router)
app.include_router(komoditas.router)
app.include_router(harga.router)
app.include_router(produksi.router)
app.include_router(admin.router)
app.include_router(distribusi.router)

@app.get("/")
def root():
    return {"app": "Sumut Agri API", "status": "active", "version": "1.0.0"}