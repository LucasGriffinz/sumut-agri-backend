from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import User, Komoditas, Produksi, HargaHarian, Distribusi
from app.routers import users, komoditas, harga, produksi, admin, distribusi

app = FastAPI(
    title="Sumut Agri API",
    description="Sistem Pemantauan Komoditas Pertanian Sumatera Utara",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router
app.include_router(users.router)
app.include_router(komoditas.router)
app.include_router(harga.router)
app.include_router(produksi.router)
app.include_router(admin.router)
app.include_router(distribusi.router)

# PENTING: create_all dipindahkan ke dalam event startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"app": "Sumut Agri API", "status": "active", "version": "1.0.0"}