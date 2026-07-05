from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import User, Komoditas, Produksi, HargaHarian, Distribusi
from app.routers import users, komoditas, harga, produksi, admin, distribusi

# Buat tabel (otomatis saat startup)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sumut Agri API",
    description="Sistem Pemantauan Komoditas Pertanian Sumatera Utara",
    version="1.0.0"
)

# ===== MIDDLEWARE CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],   # URL frontend React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(users.router)
app.include_router(komoditas.router)
app.include_router(harga.router)
app.include_router(produksi.router)
app.include_router(admin.router)
app.include_router(distribusi.router)

@app.get("/")
def root():
    return {"app": "Sumut Agri API", "status": "active", "version": "1.0.0"}

@app.get("/create-tables")
def create_tables():
    Base.metadata.create_all(bind=engine)
    return {"message": "Semua tabel berhasil dibuat"}