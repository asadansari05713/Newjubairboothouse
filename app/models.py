from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
import json
from datetime import datetime

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # This will store the hashed password

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # Required by existing database
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # This will store the hashed password
    whatsapp = Column(String(20), nullable=True)
    created_at = Column(String(50), nullable=True)  # Required by existing database
    updated_at = Column(String(50), nullable=True)  # Required by existing database
    
    # Relationships
    favourites = relationship("UserFavourite", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    status = Column(String(20), default="Available", nullable=False)  # Available or Out of Stock
    image_url = Column(String(255), nullable=True)
    images = Column(Text, nullable=True)  # JSON array of uploaded image paths
    sizes = Column(Text, nullable=True)  # JSON array of available sizes
    
    # Relationships
    favourited_by = relationship("UserFavourite", back_populates="product")
    
    def get_images_list(self):
        """Get uploaded images as a list, excluding the main image_url to avoid duplication"""
        images = []
        
        # Only return uploaded images from the images field
        if self.images:
            try:
                uploaded_images = json.loads(self.images)
                if isinstance(uploaded_images, list):
                    images.extend(uploaded_images)
            except (json.JSONDecodeError, TypeError):
                pass
            
        return images
    
    def get_sizes_list(self):
        """Get available sizes as a list"""
        sizes = []
        
        if self.sizes:
            try:
                sizes_data = json.loads(self.sizes)
                if isinstance(sizes_data, list):
                    sizes.extend(sizes_data)
            except (json.JSONDecodeError, TypeError):
                pass
            
        return sizes
    
    def has_size(self, size):
        """Check if a specific size is available"""
        return size in self.get_sizes_list()

class UserFavourite(Base):
    __tablename__ = "user_favourites"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_email = Column(String(100), nullable=True)  # Keep for backward compatibility
    created_at = Column(String(50), nullable=True)  # Keep for backward compatibility
    
    # Relationships
    user = relationship("User", back_populates="favourites")
    product = relationship("Product", back_populates="favourited_by")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), nullable=False)
    user_type = Column(String(20), nullable=False)  # "admin" or "user"
    user_id = Column(Integer, nullable=True)  # For user sessions
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)  # 1 for active, 0 for inactive

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
