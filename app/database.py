import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Railway akan set DATABASE_URL secara otomatis jika Anda menambah plugin PostgreSQL
# Untuk SQLite sementara, kita gunakan path khusus
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sumut_agri.db")

# Jika pakai SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Jika pakai PostgreSQL nanti
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()