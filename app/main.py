from fastapi import FastAPI, Request, Depends, status, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.database import engine, Base, get_db, SessionLocal
from app.routers import auth, products
import uvicorn
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI(
    title="Jubair Boot House",
    description="Professional footwear store with admin management",
    version="1.0.0"
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(auth.router)
app.include_router(products.router)

# Templates
templates = Jinja2Templates(directory="templates")

# Allowed origins (CORS)
allowed_origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
render_url = os.getenv("RENDER_EXTERNAL_URL")
if render_url:
    allowed_origins.append(render_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=500)

trusted_hosts = ["*"]
if render_url and "://" in render_url:
    host = render_url.split("://", 1)[1]
    trusted_hosts = [host]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

# Ensure tables exist
@app.on_event("startup")
def init_tables():
    Base.metadata.create_all(bind=engine)

# Ensure admin exists
@app.on_event("startup")
def ensure_admin_user():
    from app.models import Admin
    from app.routers.auth import get_password_hash

    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    db: Session = SessionLocal()
    try:
        existing = db.query(Admin).first()
        if not existing:
            admin = Admin(username=admin_username, password=get_password_hash(admin_password))
            db.add(admin)
            db.commit()
            print("✅ Admin user created:", admin_username)
        else:
            print("ℹ Admin user already exists")
    finally:
        db.close()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/catalog", response_class=HTMLResponse)
async def catalog_redirect():
    return RedirectResponse(url="/products/")

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard_redirect():
    return RedirectResponse(url="/products/admin/dashboard")

@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users_redirect():
    return RedirectResponse(url="/auth/admin/users")

if _name_ == "_main_":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=os.getenv("RELOAD", "false").lower() == "true")
