from fastapi import FastAPI, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from app.database import engine, Base, get_db
from app.routers import auth, products
import uvicorn
from starlette.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from sqlalchemy.orm import Session
import os
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

# Database tables are managed by init_schema.py
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Jubair Boot House",
    description="Professional footwear store with admin management",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(products.router)

# Templates
templates = Jinja2Templates(directory="templates")

# Note: Session management is now handled client-side via JavaScript
# The middleware has been removed to improve performance
# Security & performance middleware
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

@app.on_event("startup")
def ensure_admin_user():
    """Create initial admin from env if none exists."""
    from sqlalchemy.orm import Session as OrmSession
    from app.database import SessionLocal
    from app.models import Admin
    from app.routers.auth import get_password_hash

    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_username or not admin_password:
        return

    db: OrmSession = SessionLocal()
    try:
        existing = db.query(Admin).first()
        if not existing:
            admin = Admin(username=admin_username, password=get_password_hash(admin_password))
            db.add(admin)
            db.commit()
    finally:
        db.close()

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Home page with hero banner and categories"""
    return templates.TemplateResponse("home.html", {
        "request": request
    })

@app.get("/catalog", response_class=HTMLResponse)
async def catalog_redirect(request: Request):
    """Redirect /catalog to /products/"""
    return RedirectResponse(url="/products/")

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard_redirect(request: Request):
    """Redirect /admin/dashboard to /products/admin/dashboard"""
    return RedirectResponse(url="/products/admin/dashboard")

@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users_redirect(request: Request):
    """Redirect /admin/users to /auth/admin/users"""
    return RedirectResponse(url="/auth/admin/users")

@app.get("/size-guide", response_class=HTMLResponse)
async def size_guide_page(request: Request):
    """Size guide page with shoe sizing information"""
    return templates.TemplateResponse("size_guide.html", {
        "request": request
    })

@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Contact page with contact form and information"""
    return templates.TemplateResponse("contact.html", {
        "request": request
    })

@app.post("/contact", response_class=HTMLResponse)
async def submit_contact(request: Request, db: Session = Depends(get_db)):
    """Handle contact form submission"""
    form = await request.form()
    
    try:
        # Extract form data
        first_name = form.get("firstName", "")
        last_name = form.get("lastName", "")
        email = form.get("email", "")
        phone = form.get("phone", "")
        subject = form.get("subject", "")
        message = form.get("message", "")
        
        # Combine first and last name
        full_name = f"{first_name} {last_name}".strip()
        
        # Create feedback record
        from app.models import Feedback
        feedback = Feedback(
            name=full_name,
            email=email,
            message=f"Subject: {subject}\nPhone: {phone}\n\nMessage:\n{message}"
        )
        
        db.add(feedback)
        db.commit()
        
        # Return success response
        return templates.TemplateResponse("contact.html", {
            "request": request,
            "success": "Thank you for your message! We will get back to you within 24 hours."
        })
        
    except Exception as e:
        db.rollback()
        print(f"Error saving feedback: {e}")
        return templates.TemplateResponse("contact.html", {
            "request": request,
            "error": "Sorry, there was an error sending your message. Please try again."
        })

@app.get("/admin/feedback", response_class=HTMLResponse)
async def admin_feedback_page(request: Request, db: Session = Depends(get_db)):
    """Admin feedback management page"""
    try:
        # Check if user is admin
        from app.routers.auth import get_current_admin
        current_admin = get_current_admin(request, db)
        
        if not current_admin:
            return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
        
        # Get all feedback with error handling
        from app.models import Feedback
        
        # First, let's check what's in the database
        all_feedback = db.query(Feedback).all()
        print(f"DEBUG: Raw feedback count: {len(all_feedback)}")
        
        # Check for any None created_at values
        for fb in all_feedback:
            print(f"DEBUG: Feedback ID {fb.id}: created_at = {fb.created_at}")
        
        # Order by created_at, handling None values
        feedback_list = db.query(Feedback).filter(
            Feedback.created_at.isnot(None)
        ).order_by(Feedback.created_at.desc()).all()
        
        print(f"DEBUG: Filtered feedback count: {len(feedback_list)}")
        
        return templates.TemplateResponse("feedback.html", {
            "request": request,
            "feedback_list": feedback_list
        })
    except Exception as e:
        print(f"ERROR in admin_feedback_page: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/admin/feedback/{feedback_id}")
async def get_feedback_detail(feedback_id: int, request: Request, db: Session = Depends(get_db)):
    """Get individual feedback details for modal"""
    # Check if user is admin
    from app.routers.auth import get_current_admin
    current_admin = get_current_admin(request, db)
    
    if not current_admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Get feedback by ID
    from app.models import Feedback
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    return {
        "id": feedback.id,
        "name": feedback.name,
        "email": feedback.email,
        "message": feedback.message,
        "created_at": feedback.created_at.isoformat() if feedback.created_at else None
    }

@app.delete("/admin/feedback/{feedback_id}")
async def delete_feedback(feedback_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete feedback by ID"""
    
    # Check if user is admin
    from app.routers.auth import get_current_admin
    current_admin = get_current_admin(request, db)
    
    if not current_admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Get feedback by ID
    from app.models import Feedback
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    try:
        # Delete the feedback
        db.delete(feedback)
        db.commit()
        
        return {"success": True, "message": "Feedback deleted successfully"}
        
    except Exception as e:
        db.rollback()
        print(f"Error deleting feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete feedback")

@app.delete("/admin/feedback/clear-old")
async def clear_old_feedback(request: Request, db: Session = Depends(get_db)):
    """Clear feedback older than 30 days"""
    
    # Check if user is admin
    from app.routers.auth import get_current_admin
    current_admin = get_current_admin(request, db)
    
    if not current_admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        from datetime import datetime, timedelta
        from app.models import Feedback
        
        # Calculate date 30 days ago
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # Delete old feedback
        deleted_count = db.query(Feedback).filter(
            Feedback.created_at < thirty_days_ago
        ).delete()
        
        db.commit()
        
        return {
            "success": True, 
            "message": f"Cleared {deleted_count} old feedback entries",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error clearing old feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear old feedback")

@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """About Us page with company information"""
    return templates.TemplateResponse("about.html", {
        "request": request
    })

@app.get("/shipping", response_class=HTMLResponse)
async def shipping_page(request: Request):
    """Shipping information page"""
    return templates.TemplateResponse("shipping.html", {
        "request": request
    })

@app.get("/returns", response_class=HTMLResponse)
async def returns_page(request: Request):
    """Returns and exchange policy page"""
    return templates.TemplateResponse("returns.html", {
        "request": request
    })

@app.get("/faq", response_class=HTMLResponse)
async def faq_page(request: Request):
    """Frequently asked questions page"""
    return templates.TemplateResponse("faq.html", {
        "request": request
    })

@app.get("/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    """Privacy policy page"""
    return templates.TemplateResponse("privacy.html", {
        "request": request
    })

@app.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request):
    """Terms of service page"""
    return templates.TemplateResponse("terms.html", {
        "request": request
    })

@app.get("/cookies", response_class=HTMLResponse)
async def cookies_page(request: Request):
    """Cookie policy page"""
    return templates.TemplateResponse("cookies.html", {
        "request": request
    })

# Debug/test routes removed for production

if _name_ == "_main_":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("RELOAD", "false").lower() == "true"
