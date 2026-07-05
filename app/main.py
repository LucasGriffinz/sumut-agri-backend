import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Sumut Agri API",
    docs_url=None,      # Matikan default docs agar tidak bisa diakses langsung
    redoc_url=None,     # Matikan default redoc
    openapi_url=None,   # Matikan default openapi.json
    lifespan=lifespan
)

security = HTTPBasic()

# Ganti dengan username & password yang Anda inginkan (sebaiknya taruh di env variable)
SWAGGER_USER = os.getenv("SWAGGER_USER", "admin_sumut")
SWAGGER_PASS = os.getenv("SWAGGER_PASS", "RahasiaAgri2026")

def authenticate_swagger(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != SWAGGER_USER or credentials.password != SWAGGER_PASS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Buat route custom untuk docs yang dilindungi auth
@app.get("/docs", include_in_schema=False)
async def overridden_swagger(username: str = Depends(authenticate_swagger)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title=app.title + " - Swagger UI")

# Buat route custom untuk openapi.json yang dilindungi auth
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(username: str = Depends(authenticate_swagger)):
    return get_openapi(title=app.title, version=app.version, routes=app.routes)