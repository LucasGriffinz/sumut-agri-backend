import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Railway akan otomatis set DATABASE_URL jika PostgreSQL plugin terpasang
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sumut_agri.db")

if "postgresql" in DATABASE_URL:
    # PostgreSQL
    engine = create_engine(DATABASE_URL)
else:
    # SQLite (fallback untuk development lokal)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()