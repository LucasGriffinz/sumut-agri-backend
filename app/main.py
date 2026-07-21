import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

# Pastikan folder root proyek masuk ke path Python (Menghindari ModuleNotFoundError di lokal)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
# Import models dengan alias agar memicu pendaftaran metadata SQLAlchemy ke Base
import app.models as models  
from app.routers import users, komoditas, harga, produksi, admin, distribusi

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Baris ini akan otomatis membuat tabel di PostgreSQL lokal (jika belum ada)
    # Saat di Railway, tabel juga otomatis tersinkronisasi dengan aman
    Base.metadata.create_all(bind=engine)
    yield

# Matikan Docs bawaan karena kita akan buat Docs Custom yang dikunci password
app = FastAPI(
    title="Sumut Agri API",
    docs_url=None,       
    redoc_url=None,      
    openapi_url=None,    
    lifespan=lifespan
)

# Setup Keamanan Dokumentasi API (HTTP Basic Auth)
security = HTTPBasic()
SWAGGER_USER = os.getenv("SWAGGER_USER", "admin_sumut@gmail.com")
SWAGGER_PASS = os.getenv("SWAGGER_PASS", "RahasiaAgri2026")

def authenticate_swagger(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != SWAGGER_USER or credentials.password != SWAGGER_PASS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to API Docs",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Endpoint Docs buatan sendiri yang dilindungi Password
@app.get("/docs", include_in_schema=False)
async def overridden_swagger(username: str = Depends(authenticate_swagger)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title=app.title + " - Swagger UI")

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(username: str = Depends(authenticate_swagger)):
    return get_openapi(title=app.title, version=app.version, routes=app.routes)

# CORS (Mengizinkan komunikasi dari Android maupun Web Admin Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrasi Router Komponen API Sumut Agri
app.include_router(users.router)
app.include_router(komoditas.router)
app.include_router(harga.router)
app.include_router(produksi.router)
app.include_router(admin.router)
app.include_router(distribusi.router)
app.include_router(wilayah.router)

@app.get("/")
def root():
    return {"app": "Sumut Agri API", "status": "active", "version": "1.0.0"}