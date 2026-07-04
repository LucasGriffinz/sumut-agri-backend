from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Distribusi

router = APIRouter(prefix="/api/distribusi", tags=["Distribusi"])

@router.get("/")
def get_all(db: Session = Depends(get_db)):
    return db.query(Distribusi).all()