# Ganti response_model menjadi schemas.LoginResponse
@router.post("/api/users/login", response_model=schemas.LoginResponse)
def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    # 1. Jalankan logika verifikasi user dari database...
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    
    # 2. Generate access token...
    access_token = create_access_token(data={"sub": user.email})
    
    # 3. Kembalikan data dengan struktur yang sesuai schema baru
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user # SQLAlchemy object 'user' otomatis dikonversi ke format 'UserOut' (termasuk ID-nya) oleh Pydantic
    }