from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import get_db
from app.models import Admin, User, UserFavourite, Product, Session
import secrets
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = Jinja2Templates(directory="templates")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Session configuration
SESSION_DURATION_DAYS = 7
SESSION_DURATION_SECONDS = SESSION_DURATION_DAYS * 24 * 60 * 60

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_session(username, user_type="admin", user_id=None, db=None):
    """Create a new session in the database"""
    session_id = secrets.token_urlsafe(32)
    expiry = datetime.now() + timedelta(days=SESSION_DURATION_DAYS)
    
    # Create session in database
    new_session = Session(
        session_id=session_id,
        username=username,
        user_type=user_type,
        user_id=user_id,
        expires_at=expiry,
        is_active=1
    )
    
    if db:
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
    
    return session_id

def is_session_valid(session_data):
    """Check if session is still valid"""
    if not session_data:
        return False
    
    # Check if session is active
    if not session_data.is_active:
        return False
    
    # Check if session has expired
    return datetime.now() < session_data.expires_at

def get_current_admin(request: Request, db: Session = None):
    session_id = request.cookies.get("session_id")
    if not session_id or not db:
        return None
    
    session_data = db.query(Session).filter(
        Session.session_id == session_id,
        Session.user_type == "admin",
        Session.is_active == 1
    ).first()
    
    if not session_data or not is_session_valid(session_data):
        # Mark session as inactive if expired
        if session_data:
            session_data.is_active = 0
            db.commit()
        return None
    
    return session_data

def get_current_user(request: Request, db: Session = None):
    session_id = request.cookies.get("user_session_id")
    if not session_id or not db:
        return None
    
    session_data = db.query(Session).filter(
        Session.session_id == session_id,
        Session.user_type == "user",
        Session.is_active == 1
    ).first()
    
    if not session_data or not is_session_valid(session_data):
        # Mark session as inactive if expired
        if session_data:
            session_data.is_active = 0
            db.commit()
        return None
    
    return session_data

def get_current_session(request: Request, db: Session = None):
    # Check for admin session first
    admin_session = get_current_admin(request, db)
    if admin_session:
        return admin_session
    
    # Check for user session
    user_session = get_current_user(request, db)
    if user_session:
        return user_session
    
    return None

def refresh_session(session_id, user_type="admin", db=None):
    """Refresh session expiry"""
    if not db:
        return None
    
    session_data = db.query(Session).filter(
        Session.session_id == session_id,
        Session.user_type == user_type,
        Session.is_active == 1
    ).first()
    
    if session_data:
        session_data.expires_at = datetime.now() + timedelta(days=SESSION_DURATION_DAYS)
        db.commit()
        return session_data
    
    return None

@router.get("/session/status")
async def get_session_status(request: Request, db: Session = Depends(get_db)):
    """Get current session status for client-side validation"""
    current_session = get_current_session(request, db)
    
    if current_session:
        # Refresh session if valid
        session_id = None
        if current_session.user_type == "admin":
            session_id = request.cookies.get("session_id")
        else:
            session_id = request.cookies.get("user_session_id")
        
        if session_id:
            refresh_session(session_id, current_session.user_type, db)
        
        # For regular users, get their actual name from the User model
        display_name = current_session.username
        if current_session.user_type == "user":
            user = db.query(User).filter(User.id == current_session.user_id).first()
            if user and user.name:
                display_name = user.name
            elif user:
                display_name = user.email.split('@')[0]  # Fallback to email prefix
        
        return JSONResponse({
            "logged_in": True,
            "user_type": current_session.user_type,
            "username": display_name,
            "user_id": current_session.user_id
        })
    
    return JSONResponse({
        "logged_in": False,
        "user_type": None,
        "username": None,
        "user_id": None
    })

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    # Check if admin is already logged in
    current_session = get_current_admin(request, db)
    if current_session:
        # Admin is already logged in, redirect to dashboard
        return RedirectResponse(url="/products/admin/dashboard", status_code=status.HTTP_302_FOUND)
    
    # Admin is not logged in, show login page
    return templates.TemplateResponse("admin_login.html", {"request": request})

@router.get("/user/login", response_class=HTMLResponse)
async def user_login_page(request: Request, db: Session = Depends(get_db)):
    # Check if user is already logged in
    current_session = get_current_user(request, db)
    if current_session:
        # User is already logged in, redirect to home page
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Check for signup success and pre-fill data
    signup_success = request.query_params.get("signup") == "success"
    prefill_email = request.query_params.get("email", "")
    
    context = {
        "request": request,
        "signup_success": signup_success,
        "prefill_email": prefill_email,
        "showSignup": False
    }
    
    return templates.TemplateResponse("user_login.html", context)

@router.post("/user/login")
async def user_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Validate user credentials against database
    user = db.query(User).filter(User.email == email).first()
    
    if user and pwd_context.verify(password, user.password):
        # Create user session with user ID in database
        session_id = create_session(email, "user", user.id, db)
        
        # Redirect to home page with session cookie
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(
            key="user_session_id", 
            value=session_id, 
            httponly=True, 
            max_age=SESSION_DURATION_SECONDS,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        return response
    else:
        return templates.TemplateResponse(
            "user_login.html", 
            {"request": request, "error": "Invalid email or password", "prefill_email": email},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

@router.get("/user/signup", response_class=HTMLResponse)
async def user_signup_page(request: Request):
    return templates.TemplateResponse("user_login.html", {"request": request, "showSignup": True})

@router.post("/user/signup")
async def user_signup(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    whatsapp: str = Form(None),
    db: Session = Depends(get_db)
):
    # Validate passwords match
    if password != confirm_password:
        return templates.TemplateResponse(
            "user_signup.html", 
            {"request": request, "error": "Passwords do not match", "prefillEmail": email, "prefillName": name, "prefillWhatsapp": whatsapp},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            "user_signup.html", 
            {"request": request, "error": "User with this email already exists", "prefillEmail": email, "prefillName": name, "prefillWhatsapp": whatsapp},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Create new user
    hashed_password = pwd_context.hash(password)
    
    new_user = User(
        name=name,
        email=email,
        password=hashed_password,
        whatsapp=whatsapp,
        created_at=None,  # Will be set by database default
        updated_at=None   # Will be set by database default
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Redirect to login page with pre-filled data
        response = RedirectResponse(url="/auth/user/login?signup=success&email=" + email, status_code=status.HTTP_302_FOUND)
        return response
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {e}")  # Add debug logging
        return templates.TemplateResponse(
            "user_signup.html", 
            {"request": request, "error": "Failed to create account. Please try again.", "prefillEmail": email, "prefillName": name, "prefillWhatsapp": whatsapp},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if admin exists
    admin = db.query(Admin).filter(Admin.username == username).first()
    
    if not admin or not verify_password(password, admin.password):
        return templates.TemplateResponse(
            "admin_login.html", 
            {"request": request, "error": "Invalid username or password"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # Create session in database
    session_id = create_session(username, "admin", None, db)
    
    # Redirect to dashboard with session cookie
    response = RedirectResponse(url="/products/admin/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="session_id", 
        value=session_id, 
        httponly=True, 
        max_age=SESSION_DURATION_SECONDS,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    return response

@router.get("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if session_id:
        # Mark session as inactive in database
        session_data = db.query(Session).filter(
            Session.session_id == session_id,
            Session.user_type == "admin"
        ).first()
        if session_data:
            session_data.is_active = 0
            db.commit()
    
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="session_id")
    return response

@router.get("/user/logout")
async def user_logout(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("user_session_id")
    if session_id:
        # Mark session as inactive in database
        session_data = db.query(Session).filter(
            Session.session_id == session_id,
            Session.user_type == "user"
        ).first()
        if session_data:
            session_data.is_active = 0
            db.commit()
    
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="user_session_id")
    return response

@router.post("/user/favourites/add/{product_id}")
async def add_to_favourites(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Add product to user's favourites"""
    current_session = get_current_user(request, db)
    if not current_session:
        return {"success": False, "message": "User not logged in"}
    
    user_id = current_session.user_id
    if not user_id:
        return {"success": False, "message": "User not logged in"}
    
    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"success": False, "message": "Product not found"}
    
    # Check if already favourited
    existing_fav = db.query(UserFavourite).filter(
        UserFavourite.user_id == user_id,
        UserFavourite.product_id == product_id
    ).first()
    
    if existing_fav:
        return {"success": False, "message": "Product already in favourites"}
    
    # Add to favourites
    try:
        new_favourite = UserFavourite(user_id=user_id, product_id=product_id)
        db.add(new_favourite)
        db.commit()
        return {"success": True, "message": "Added to favourites"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": "Failed to add to favourites"}

@router.delete("/user/favourites/remove/{product_id}")
async def remove_from_favourites(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Remove product from user's favourites"""
    current_session = get_current_user(request, db)
    if not current_session:
        return {"success": False, "message": "User not logged in"}
    
    user_id = current_session.user_id
    if not user_id:
        return {"success": False, "message": "User not logged in"}
    
    # Remove from favourites
    try:
        favourite = db.query(UserFavourite).filter(
            UserFavourite.user_id == user_id,
            UserFavourite.product_id == product_id
        ).first()
        
        if favourite:
            db.delete(favourite)
            db.commit()
            return {"success": True, "message": "Removed from favourites"}
        else:
            return {"success": False, "message": "Product not in favourites"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": "Failed to remove from favourites"}

@router.get("/user/favourites/check/{product_id}")
async def check_favourite_status(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Check if a product is favourited by the current user"""
    current_session = get_current_user(request, db)
    if not current_session:
        return {"is_favourited": False, "message": "User not logged in"}
    
    user_id = current_session.user_id
    if not user_id:
        return {"is_favourited": False, "message": "User not logged in"}
    
    # Check if product is favourited
    favourite = db.query(UserFavourite).filter(
        UserFavourite.user_id == user_id,
        UserFavourite.product_id == product_id
    ).first()
    
    return {"is_favourited": favourite is not None}

@router.get("/user/profile", response_class=HTMLResponse)
async def user_profile(request: Request, db: Session = Depends(get_db)):
    """User profile page with favourites"""
    current_session = get_current_user(request, db)
    if not current_session:
        return RedirectResponse(url="/auth/user/login", status_code=status.HTTP_302_FOUND)
    
    # Get user's favourite products
    user_id = current_session.user_id
    if not user_id:
        return RedirectResponse(url="/auth/user/login", status_code=status.HTTP_302_FOUND)
    
    # Get complete user data from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/auth/user/login", status_code=status.HTTP_302_FOUND)
    
    favourites = db.query(UserFavourite).filter(UserFavourite.user_id == user_id).all()
    favourite_products = [fav.product for fav in favourites]
    
    return templates.TemplateResponse("user_profile.html", {
        "request": request,
        "current_session": {
            "username": user.name or user.email,  # Use name if available, otherwise email
            "email": user.email,
            "name": user.name,
            "whatsapp": user.whatsapp,
            "created_at": user.created_at,
            "user_id": user.id,
            "type": current_session.user_type
        },
        "favourites": favourite_products
    })

@router.get("/user/favourites", response_class=HTMLResponse)
async def user_favourites(request: Request, db: Session = Depends(get_db)):
    """User favourites page"""
    current_session = get_current_user(request, db)
    if not current_session:
        return RedirectResponse(url="/auth/user/login", status_code=status.HTTP_302_FOUND)
    
    # Get user's favourite products
    user_id = current_session.user_id
    if not user_id:
        return RedirectResponse(url="/auth/user/login", status_code=status.HTTP_302_FOUND)
    
    # Get complete user data from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/auth/user/login", status_code=status.HTTP_302_FOUND)
    
    favourites = db.query(UserFavourite).filter(UserFavourite.user_id == user_id).all()
    favourite_products = [fav.product for fav in favourites]
    
    return templates.TemplateResponse("user_favourites.html", {
        "request": request,
        "current_session": {
            "username": user.name or user.email,  # Use name if available, otherwise email
            "email": user.email,
            "name": user.name,
            "whatsapp": user.whatsapp,
            "created_at": user.created_at,
            "user_id": user.id,
            "type": current_session.user_type
        },
        "favourites": favourite_products
    })

@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request, db: Session = Depends(get_db)):
    """Admin users page - only accessible to admins"""
    current_session = get_current_admin(request, db)
    if not current_session:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    # Get all users
    users = db.query(User).all()
    
    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "current_session": {
            "username": current_session.username,
            "type": current_session.user_type
        },
        "users": users
    })

@router.post("/user/profile/update")
async def update_user_profile(
    request: Request,
    name: str = Form(...),
    whatsapp: str = Form(None),
    db: Session = Depends(get_db)
):
    """Update user profile information"""
    current_session = get_current_user(request, db)
    if not current_session:
        return JSONResponse(
            {"success": False, "message": "User not authenticated"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Update user in database
        user = db.query(User).filter(User.id == current_session.user_id).first()
        if not user:
            return JSONResponse(
                {"success": False, "message": "User not found"},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        user.name = name
        user.whatsapp = whatsapp
        user.updated_at = datetime.now()
        
        db.commit()
        db.refresh(user)
        
        return JSONResponse({
            "success": True,
            "message": "Profile updated successfully",
            "data": {
                "name": user.name,
                "whatsapp": user.whatsapp,
                "email": user.email,
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None
            }
        })
        
    except Exception as e:
        db.rollback()
        print(f"Error updating user profile: {e}")
        return JSONResponse(
            {"success": False, "message": "Failed to update profile"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/setup")
async def setup_admin(db: Session = Depends(get_db)):
    """Setup initial admin user (run once)"""
    try:
        # Check if admin already exists
        existing_admin = db.query(Admin).first()
        if existing_admin:
            return {"message": "Admin already exists"}
        
        # Create default admin
        admin = Admin(
            username="JuberSiddique",
            password=get_password_hash("Juber@708492")
        )
        db.add(admin)
        db.commit()
        return {"message": "Admin created successfully", "username": "JuberSiddique", "password": "Juber@708492"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
