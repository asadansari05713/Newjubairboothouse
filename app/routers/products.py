from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query, status, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.models import Product
from app.routers.auth import get_current_admin, get_current_session
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from typing import Optional, List
import os
import json
import uuid
from datetime import datetime
from collections import defaultdict
from sqlalchemy import func

router = APIRouter(prefix="/products", tags=["Products"])
templates = Jinja2Templates(directory="templates")

# Product categories
CATEGORIES = ["Sports", "Casual", "Formal", "Boots", "Sneakers", "Sandals"]
SIZES = ["6", "7", "8", "9", "10", "11", "12"]
STATUSES = ["Available", "Out of Stock"]

# Ensure uploads directory exists
UPLOADS_DIR = "static/uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Analytics file storage (for search counts)
ANALYTICS_DIR = "analytics"
SEARCH_STATS_FILE = os.path.join(ANALYTICS_DIR, "search_stats.json")
GENDER_MAP_FILE = os.path.join(ANALYTICS_DIR, "gender_map.json")
os.makedirs(ANALYTICS_DIR, exist_ok=True)

def _load_search_stats() -> dict:
    try:
        if os.path.exists(SEARCH_STATS_FILE):
            with open(SEARCH_STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"WARN: failed to load search stats: {e}")
    return {}

def _save_search_stats(stats: dict) -> None:
    try:
        with open(SEARCH_STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f)
    except Exception as e:
        print(f"WARN: failed to save search stats: {e}")

def _increment_search_counts(product_ids: List[int]):
    if not product_ids:
        return
    stats = _load_search_stats()
    for pid in product_ids:
        key = str(pid)
        stats[key] = int(stats.get(key, 0)) + 1
    _save_search_stats(stats)

def _load_gender_map() -> dict:
    try:
        if os.path.exists(GENDER_MAP_FILE):
            with open(GENDER_MAP_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"WARN: failed to load gender map: {e}")
    return {}

def _save_gender_map(gmap: dict) -> None:
    try:
        with open(GENDER_MAP_FILE, "w", encoding="utf-8") as f:
            json.dump(gmap, f)
    except Exception as e:
        print(f"WARN: failed to save gender map: {e}")

def save_uploaded_file(file: UploadFile) -> str:
    """Save uploaded file and return the file path"""
    try:
        print(f"DEBUG: Starting file upload for: {file.filename}")
        print(f"DEBUG: File content type: {file.content_type}")
        print(f"DEBUG: File size: {file.size if hasattr(file, 'size') else 'Unknown'}")
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOADS_DIR, unique_filename)
        
        print(f"DEBUG: Generated filename: {unique_filename}")
        print(f"DEBUG: Full file path: {file_path}")
        print(f"DEBUG: Uploads directory exists: {os.path.exists(UPLOADS_DIR)}")
        print(f"DEBUG: Uploads directory writable: {os.access(UPLOADS_DIR, os.W_OK)}")
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        print(f"DEBUG: File saved successfully to: {file_path}")
        print(f"DEBUG: File exists after save: {os.path.exists(file_path)}")
        
        return f"/static/uploads/{unique_filename}"
    except Exception as e:
        print(f"ERROR in save_uploaded_file: {e}")
        import traceback
        traceback.print_exc()
        raise e

@router.get("/", response_class=HTMLResponse)
async def catalog_page(
    request: Request,
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
    , db: Session = Depends(get_db)
):
    """Product catalog page with search and filters"""
    try:
        from sqlalchemy import or_, and_
        # Build SQLAlchemy query
        base_query = db.query(Product)

        # Apply exact filters first
        if category:
            base_query = base_query.filter(Product.category.ilike(f"%{category}%"))
        if status:
            base_query = base_query.filter(Product.status == status)

        products = []

        if search and search.strip():
            # Case-insensitive, partial matching across name, description, and category
            raw = search.strip()
            tokens = [t for t in raw.replace("/", " ").replace("-", " ").split() if t]

            # 1) Try full-string match across fields
            full_cond = or_(
                Product.name.ilike(f"%{raw}%"),
                Product.description.ilike(f"%{raw}%"),
                Product.category.ilike(f"%{raw}%")
            )
            query1 = base_query.filter(full_cond)
            products = query1.order_by(Product.id).all()

            # 2) If nothing, try token-wise OR across fields
            if not products and tokens:
                token_ors = []
                for tok in tokens:
                    token_ors.append(Product.name.ilike(f"%{tok}%"))
                    token_ors.append(Product.description.ilike(f"%{tok}%"))
                    token_ors.append(Product.category.ilike(f"%{tok}%"))
                query2 = base_query.filter(or_(*token_ors))
                products = query2.order_by(Product.id).all()

            # 3) If still nothing, loosen to any product (closest related):
            #    Prefer products in the same category if category was given, else recent ones
            if not products:
                if category:
                    products = db.query(Product).filter(Product.category.ilike(f"%{category}%")).order_by(Product.id).all()
                else:
                    products = db.query(Product).order_by(Product.id.desc()).limit(12).all()

            # Update analytics: increment search count for products shown for this search
            try:
                _increment_search_counts([p.id for p in products])
            except Exception as e:
                print(f"WARN: failed to increment search counts: {e}")
        else:
            # No search text: just list with filters
            products = base_query.order_by(Product.id).all()
        
        # Debug: Print product information
        print(f"DEBUG: Found {len(products)} products in catalog")
        for p in products:
            print(f"DEBUG: Product ID: {p.id}, Name: {p.name}")

        # Unique categories for filter dropdown
        categories = [row[0] for row in db.query(Product.category).distinct().all() if row[0]]
        
        return templates.TemplateResponse("catalog.html", {
            "request": request,
            "products": products,
            "categories": categories,
            "current_search": search,
            "current_category": category,
            "current_status": status
        })
        
    except Exception as e:
        print(f"Error loading catalog: {e}")
        return templates.TemplateResponse("catalog.html", {
            "request": request,
            "products": [],
            "categories": [],
            "error": "Error loading products"
        })

@router.get("/admin/analytics", response_class=HTMLResponse)
async def admin_analytics(request: Request, db: Session = Depends(get_db)):
    """Admin analytics: top searched and favourited products"""
    current_admin = get_current_admin(request, db)
    if not current_admin:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    try:
        # Load search counts
        search_stats = _load_search_stats()  # {product_id(str): count}

        # Favourite counts via aggregate
        fav_counts = dict(
            db.query(UserFavourite.product_id, func.count(UserFavourite.id))
              .group_by(UserFavourite.product_id)
              .all()
        )

        # Build combined rows for all products that have either metric
        product_ids = set(int(pid) for pid in search_stats.keys()) | set(fav_counts.keys())
        # Also include all products to show zeros for others (optional)
        all_products = db.query(Product).all()
        product_map = {p.id: p for p in all_products}
        rows = []
        for pid, product in product_map.items():
            searches = int(search_stats.get(str(pid), 0))
            favs = int(fav_counts.get(pid, 0))
            rows.append({
                "id": pid,
                "name": product.name,
                "searches": searches,
                "favourites": favs
            })

        # Sort by searches desc, then favourites desc
        rows.sort(key=lambda r: (r["searches"], r["favourites"]), reverse=True)

        # Top 5 for chart
        top5 = rows[:5]
        chart_labels = [r["name"] for r in top5]
        chart_data = [r["searches"] for r in top5]

        return templates.TemplateResponse("analytics.html", {
            "request": request,
            "rows": rows,
            "chart_labels": chart_labels,
            "chart_data": chart_data
        })
    except Exception as e:
        print(f"Error loading analytics: {e}")
        return templates.TemplateResponse("analytics.html", {
            "request": request,
            "rows": [],
            "chart_labels": [],
            "chart_data": []
        })

@router.get("/{product_id}", response_class=HTMLResponse)
async def product_detail(product_id: int, request: Request, db: Session = Depends(get_db)):
    """Product detail page"""
    try:
        # Debug: Print all product IDs
        all_products = db.query(Product).all()
        print(f"DEBUG: All products in database: {[p.id for p in all_products]}")
        print(f"DEBUG: Looking for product ID: {product_id}")
        
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            print(f"DEBUG: Product with ID {product_id} not found")
            raise HTTPException(status_code=404, detail="Product not found")
        
        print(f"DEBUG: Found product: {product.name} (ID: {product.id})")
        
        # Get related products (same category, excluding current product)
        related_products = db.query(Product).filter(
            Product.category == product.category,
            Product.id != product.id
        ).limit(4).all()
        
        print(f"DEBUG: Found {len(related_products)} related products")
        
        return templates.TemplateResponse("product_detail.html", {
            "request": request,
            "product": product,
            "related_products": related_products
        })
        
    except Exception as e:
        print(f"Error loading product detail: {e}")
        raise HTTPException(status_code=404, detail="Product not found")

@router.get("/debug/list", response_class=HTMLResponse)
async def debug_products_list(request: Request, db: Session = Depends(get_db)):
    """Debug route to list all products"""
    try:
        products = db.query(Product).order_by(Product.id).all()
        product_list = []
        for p in products:
            product_list.append(f"ID: {p.id}, Name: {p.name}, Category: {p.category}")
        
        return HTMLResponse(f"""
        <html>
        <head><title>Product Debug</title></head>
        <body>
            <h1>Products in Database</h1>
            <p>Total products: {len(products)}</p>
            <ul>
                {"".join([f"<li>{p}</li>" for p in product_list])}
            </ul>
            <p><a href="/products/">Back to Catalog</a></p>
        </body>
        </html>
        """)
    except Exception as e:
        return HTMLResponse(f"""
        <html>
        <head><title>Product Debug Error</title></head>
        <body>
            <h1>Error</h1>
            <p>{str(e)}</p>
            <p><a href="/products/">Back to Catalog</a></p>
        </body>
        </html>
        """)

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    show_add: bool = Query(False),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Admin dashboard for product management"""
    current_admin = get_current_admin(request, db)
    
    if not current_admin:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    try:
        # Build query with optional filters for admin view
        query = db.query(Product)
        if search:
            query = query.filter(Product.name.ilike(f"%{search}%"))
        if category:
            query = query.filter(Product.category == category)
        if status:
            query = query.filter(Product.status == status)

        # Get products ordered by ID to maintain consistent positions
        products = query.order_by(Product.id).all()
        
        # Get statistics
        total_products = len(products)
        available_products = len([p for p in products if p.status == "Available"])
        out_of_stock = len([p for p in products if p.status == "Out of Stock"])
        
        # Get products by category
        category_stats = {}
        for product in products:
            category = product.category
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += 1
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "products": products,
            "total_products": total_products,
            "available_products": available_products,
            "out_of_stock": out_of_stock,
            "category_stats": category_stats,
            "categories": CATEGORIES,
            "statuses": STATUSES,
            "show_add": show_add,
            "current_search": search,
            "current_category": category,
            "current_status": status
        })
        
    except Exception as e:
        print(f"Error loading admin dashboard: {e}")
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "products": [],
            "error": "Error loading dashboard",
            "categories": CATEGORIES,
            "statuses": STATUSES,
            "show_add": show_add,
            "current_search": search,
            "current_category": category,
            "current_status": status
        })

@router.get("/admin/add", response_class=HTMLResponse)
async def add_product_page(request: Request, db: Session = Depends(get_db)):
    """Add product page - redirects to dashboard with modal"""
    current_admin = get_current_admin(request, db)
    
    if not current_admin:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    # Redirect to dashboard - the add form is in a modal there
    return RedirectResponse(url="/products/admin/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/admin/add")
async def add_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    category: str = Form(...),
    gender: str = Form(...),
    status: str = Form(...),
    image_url: str = Form(None),
    sizes: List[str] = Form([]),
    images: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    """Add new product"""
    current_admin = get_current_admin(request, db)
    
    if not current_admin:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    try:
        print(f"DEBUG: Add product - received {len(images)} images")
        for i, image in enumerate(images):
            print(f"DEBUG: Image {i}: filename={image.filename}, content_type={image.content_type}")
        
        # Save uploaded images
        uploaded_images = []
        for image in images:
            if image.filename:
                print(f"DEBUG: Processing image: {image.filename}")
                image_path = save_uploaded_file(image)
                uploaded_images.append(image_path)
                print(f"DEBUG: Image saved to: {image_path}")
            else:
                print(f"DEBUG: Skipping image with no filename")
        
        print(f"DEBUG: Total uploaded images: {len(uploaded_images)}")
        
        # Create product
        product = Product(
            name=name,
            description=description,
            price=price,
            category=category,
            status=status,
            image_url=image_url,
            images=json.dumps(uploaded_images) if uploaded_images else None,
            sizes=json.dumps(sizes) if sizes else None
        )
        # Persist gender in external map (since DB lacks gender column)
        try:
            gmap = _load_gender_map()
            gmap[str(product.id)] = gender
            _save_gender_map(gmap)
        except Exception as e:
            print(f"WARN: could not persist gender map (add): {e}")
        db.add(product)
        db.commit()
        
        return RedirectResponse(url="/products/admin/dashboard", status_code=status.HTTP_302_FOUND)
        
    except Exception as e:
        print(f"Error adding product: {e}")
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "products": [],
            "categories": CATEGORIES,
            "sizes": SIZES,
            "statuses": STATUSES,
            "show_add_form": True,
            "error": "Error adding product"
        })

@router.get("/admin/edit/{product_id}", response_class=HTMLResponse)
async def edit_product_page(product_id: int, request: Request, db: Session = Depends(get_db)):
    """Edit product page"""
    current_admin = get_current_admin(request, db)
    
    if not current_admin:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    try:
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Redirect to dashboard - the edit form is in a modal there
        return RedirectResponse(url="/products/admin/dashboard", status_code=status.HTTP_302_FOUND)
        
    except Exception as e:
        print(f"Error loading product for edit: {e}")
        raise HTTPException(status_code=404, detail="Product not found")

@router.post("/admin/edit/{product_id}")
async def edit_product(
    product_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    category: str = Form(...),
    product_status: str = Form(...),
    gender: Optional[str] = Form(None),
    image_url: str = Form(None),
    sizes: List[str] = Form([]),
    images: List[UploadFile] = File([]),
    images_to_remove: str = Form(None),
    db: Session = Depends(get_db)
):
    """Update product"""
    current_admin = get_current_admin(request, db)
    
    if not current_admin:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    try:
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        print(f"DEBUG: Edit product - received {len(images)} images")
        for i, image in enumerate(images):
            print(f"DEBUG: Image {i}: filename={image.filename}, content_type={image.content_type}")
        
        # Save uploaded images
        uploaded_images = []
        for image in images:
            if image.filename:
                print(f"DEBUG: Processing image: {image.filename}")
                image_path = save_uploaded_file(image)
                uploaded_images.append(image_path)
                print(f"DEBUG: Image saved to: {image_path}")
            else:
                print(f"DEBUG: Skipping image with no filename")
        
        print(f"DEBUG: Total uploaded images: {len(uploaded_images)}")
        
        # Update product
        product.name = name
        product.description = description
        product.price = price
        product.category = category
        product.status = product_status
        product.image_url = image_url
        product.sizes = json.dumps(sizes) if sizes else None
        # Persist gender tag inside description (temporary until DB column is added)
        if gender in ("Male", "Female"):
            # remove existing gender tag
            if product.description:
                product.description = product.description.replace("Gender: Male", "").replace("Gender: Female", "").strip()
            if product.description:
                product.description = f"{product.description}\nGender: {gender}".strip()
            else:
                product.description = f"Gender: {gender}"
        
        # Handle image removal first
        if images_to_remove:
            try:
                # Parse the comma-separated list of images to remove
                images_to_remove_list = [img.strip() for img in images_to_remove.split(',') if img.strip()]
                print(f"DEBUG: Images to remove: {images_to_remove_list}")
                
                # Get current images
                current_images = []
                if product.images:
                    try:
                        current_images = json.loads(product.images)
                    except Exception:
                        current_images = []
                
                # Remove the specified images
                for img_to_remove in images_to_remove_list:
                    if img_to_remove in current_images:
                        current_images.remove(img_to_remove)
                        print(f"DEBUG: Removed image: {img_to_remove}")
                        
                        # Try to delete the actual file from disk
                        try:
                            if img_to_remove.startswith('/static/uploads/'):
                                file_path = img_to_remove.replace('/static/uploads/', 'static/uploads/')
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                                    print(f"DEBUG: File {file_path} deleted from disk")
                        except Exception as e:
                            print(f"WARNING: Could not delete file from disk: {e}")
                
                # Update product images
                product.images = json.dumps(current_images) if current_images else None
                print(f"DEBUG: Updated product images: {current_images}")
                
            except Exception as e:
                print(f"ERROR: Failed to process image removal: {e}")
        
        # Add new images to existing ones
        if uploaded_images:
            existing_images = []
            if product.images:
                try:
                    existing_images = json.loads(product.images)
                except Exception:
                    existing_images = []
            product.images = json.dumps(existing_images + uploaded_images)

        db.commit()
        
        return RedirectResponse(url="/products/admin/dashboard", status_code=status.HTTP_302_FOUND)
        
    except Exception as e:
        print(f"Error updating product: {e}")
        return RedirectResponse(url="/products/admin/dashboard?error=update_failed", status_code=status.HTTP_302_FOUND)

@router.delete("/admin/remove-image/{product_id}")
async def remove_product_image(product_id: int, request: Request, image_path: str = Query(...), db: Session = Depends(get_db)):
    """Remove a specific image from a product"""
    current_admin = get_current_admin(request, db)
    
    if not current_admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        print(f"DEBUG: Removing image {image_path} from product {product_id}")
        
        # Get current images
        current_images = []
        if product.images:
            try:
                current_images = json.loads(product.images)
            except Exception:
                current_images = []
        
        # Remove the specified image
        if image_path in current_images:
            current_images.remove(image_path)
            product.images = json.dumps(current_images) if current_images else None
            db.commit()
            
            print(f"DEBUG: Image removed successfully. Remaining images: {len(current_images)}")
            
            # Try to delete the actual file
            try:
                if image_path.startswith('/static/uploads/'):
                    file_path = image_path.replace('/static/uploads/', 'static/uploads/')
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"DEBUG: File {file_path} deleted from disk")
            except Exception as e:
                print(f"WARNING: Could not delete file from disk: {e}")
            
            return {"success": True, "message": "Image removed successfully", "remaining_images": len(current_images)}
        else:
            raise HTTPException(status_code=404, detail="Image not found in product")
        
    except Exception as e:
        print(f"Error removing image: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove image")

@router.delete("/admin/delete/{product_id}")
async def delete_product(product_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete product"""
    current_admin = get_current_admin(request, db)
    
    if not current_admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Delete product
        db.delete(product)
        db.commit()
        
        return {"message": "Product deleted successfully"}
        
    except Exception as e:
        print(f"Error deleting product: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete product")

@router.post("/admin/update-status/{product_id}")
async def update_product_status(product_id: int, request: Request, status: str = Form(...), db: Session = Depends(get_db)):
    """Update product status"""
    current_admin = get_current_admin(request, db)
    
    if not current_admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Update status
        product.status = status
        db.commit()
        
        return RedirectResponse(url="/products/admin/dashboard", status_code=status.HTTP_302_FOUND)
        
    except Exception as e:
        print(f"Error updating product status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update status")
