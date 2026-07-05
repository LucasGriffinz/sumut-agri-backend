import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")

print("=" * 60)
print("DATABASE_URL =", DATABASE_URL)
print("=" * 60)

if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        echo=True
    )
else:
    print("DATABASE_URL TIDAK DITEMUKAN!")
    engine = create_engine(
        "sqlite:///./sumut_agri.db",
        connect_args={"check_same_thread": False}
    )