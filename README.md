# Jubair Boot House - Professional Footwear Store

A modern, responsive web application for managing and showcasing footwear products with advanced features including multiple image uploads, user authentication, and admin management.

## ✨ Features

### 🛍️ Product Management
- **Multiple Image Uploads**: Upload multiple images per product with drag & drop support
- **Image Gallery**: View product images in a beautiful carousel/slider
- **Hybrid Image Support**: Support for both uploaded images and external URLs
- **Product Catalog**: Responsive product grid with search and filtering
- **Product Catalog**: Browse products with search and filtering
- **Product Details**: Clickable product cards with detailed views and image galleries
- **Admin Dashboard**: Complete product management interface

### 🔐 Authentication & Security
- **Admin Authentication**: Secure admin login with password hashing
- **User Authentication**: User registration and login system
- **Session Management**: Persistent user sessions
- **Password Security**: Bcrypt password hashing

### 🎨 User Experience
- **Responsive Design**: Mobile-first, modern UI with Bootstrap 5
- **Interactive Elements**: Hover effects, animations, and smooth transitions
- **Image Previews**: Real-time image previews during upload
- **Drag & Drop**: Intuitive file upload interface
- **Toast Notifications**: User feedback for actions

### 🔍 Search & Filtering
- **Product Search**: Search products by name
- **Category Filtering**: Filter by product categories
- **Status Filtering**: Filter by availability status
- **Advanced Filters**: Size and other attribute filtering

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd jubair_boot_house
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database (PostgreSQL)**
   - Install PostgreSQL and create a database/user
   - Set environment variable before running the app:
   ```bash
   # Windows PowerShell
   $env:DATABASE_URL = "postgresql+psycopg2://username:password@localhost:5432/jubair_boot_house"
   # Linux/macOS
   export DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/jubair_boot_house
   ```

5. **Start the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   - Main site: http://localhost:8000
   - Admin dashboard: http://localhost:8000/products/admin/dashboard
   - Product catalog: http://localhost:8000/products/

## 📁 Project Structure

```
jubair_boot_house/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   └── routers/
│       ├── auth.py          # Authentication routes
│       └── products.py      # Product management routes
├── static/
│   ├── css/
│   │   └── style.css        # Custom styles
│   ├── js/
│   │   └── script.js        # Custom JavaScript
│   └── uploads/             # Uploaded product images
├── templates/
│   ├── base.html            # Base template
│   ├── home.html            # Home page
│   ├── catalog.html         # Product catalog
│   ├── product_detail.html  # Product detail page with image gallery
│   ├── dashboard.html       # Admin dashboard

│   └── auth templates...    # Authentication pages
├── requirements.txt         # Python dependencies
├── run.py                   # Application runner
└── README.md               # This file
```

## 🖼️ Multiple Images Feature

### Backend Implementation
- **Database Schema**: Added `images` column (TEXT) to store JSON array of image paths
- **File Upload**: Secure file upload handling with unique filename generation
- **Image Storage**: Images stored in `/static/uploads/` directory
- **Hybrid Support**: Both uploaded images and external URLs supported

### Frontend Implementation
- **Admin Panel**: 
  - Drag & drop image upload interface
  - Real-time image previews
  - Multiple file selection
  - Image removal functionality
  - **Login Credentials**: Username: JuberSiddique, Password: Juber@708492
- **Product Catalog**:
  - Clickable product cards
  - Shows URL image (if available) or first uploaded image
  - Image count indicators for multiple images
  


### Usage Examples

#### Adding Products with Multiple Images
1. Navigate to Admin Dashboard
2. Click "Add New Product"
3. Fill in product details
4. Upload multiple images using drag & drop or file browser
5. Optionally add an external image URL
6. Save the product

#### Viewing Product Images
1. Browse the product catalog
   - Product cards show URL image (if available) or first uploaded image
   - Image count badge indicates total number of images
2. Click on any product card to view detailed information
3. View complete image gallery with thumbnail navigation
4. Add products to cart or wishlist from the detail page

## 🔧 API Endpoints

### Product Management
- `GET /products/` - Product catalog page
- `GET /products/{id}` - Product detail page with image gallery

- `GET /products/admin/dashboard` - Admin dashboard
- `POST /products/admin/add` - Add new product with images
- `POST /products/admin/edit/{id}` - Edit product with images
- `POST /products/admin/delete/{id}` - Delete product
- `POST /products/admin/toggle-status/{id}` - Toggle stock status

### Authentication
- `GET /auth/login` - Admin login page
- `POST /auth/login` - Admin login
- `GET /auth/user/login` - User login page
- `POST /auth/user/login` - User login
- `GET /auth/user/signup` - User registration page
- `POST /auth/user/signup` - User registration
- `GET /auth/logout` - Logout

## 🛠️ Technical Details

### Database Schema
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    category VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'Available',
    image_url VARCHAR(255),
    images TEXT  -- JSON array of uploaded image paths
);
```

### File Upload Security
- File type validation (images only)
- Unique filename generation using UUID
- Secure file storage in dedicated directory
- File size limits and validation

### Image Handling
- Automatic image format detection
- Responsive image display
- Lazy loading for performance
- Fallback handling for missing images

## 🎯 Key Features

### Multiple Image Support
- ✅ Upload multiple images per product
- ✅ Drag & drop interface
- ✅ Real-time previews
- ✅ Image removal before save
- ✅ Hybrid URL + upload support
- ✅ Smart catalog display (URL image or first uploaded image)
- ✅ Complete product detail pages with image galleries
- ✅ Smooth animations and interactive features

### User Experience
- ✅ Responsive design
- ✅ Interactive product cards
- ✅ Clickable navigation to product details

- ✅ Image gallery with navigation
- ✅ Toast notifications
- ✅ Loading states

### Admin Features
- ✅ Complete product management
- ✅ Multiple image upload interface
- ✅ Image preview and management
- ✅ Product editing with image addition
- ✅ Secure file handling

## 🧪 Testing

Run the test suite to verify functionality:
```bash
python test_multiple_images.py
```

## 🔒 Security Considerations

- Password hashing with bcrypt
- File upload validation
- SQL injection prevention
- XSS protection
- CSRF protection
- Secure session management

## 🚀 Deployment

### Production Considerations
- Use a production WSGI server (Gunicorn, uvicorn)
- Configure proper static file serving
- Set up database backups
- Implement proper logging
- Configure environment variables
- Set up SSL/TLS certificates

### Environment Variables
```bash
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/jubair_boot_house
SECRET_KEY=your-secret-key-here
UPLOAD_DIR=static/uploads
MAX_FILE_SIZE=10485760  # 10MB
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact: jubersiddique33@gmail.com

---

**Built with ❤️ using FastAPI, SQLAlchemy, and Bootstrap 5**
