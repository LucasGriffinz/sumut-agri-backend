from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, UserOut
from passlib.context import CryptContext

router = APIRouter(prefix="/api/users", tags=["Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def hash_password(password):
    return pwd_context.hash(password)

@router.post("/register", response_model=UserOut)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    if data.no_hp:
        hp_exist = db.query(User).filter(User.no_hp == data.no_hp).first()
        if hp_exist:
            raise HTTPException(status_code=400, detail="No HP sudah digunakan")
    user = User(
        nama_lengkap=data.nama_lengkap,
        email=data.email,
        password_hash=hash_password(data.password),
        role="petani",   # registrasi publik otomatis sebagai petani
        no_hp=data.no_hp,
        alamat=data.alamat,
        kabupaten_kota=data.kabupaten_kota,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=UserOut)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    return user

@router.get("/", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()