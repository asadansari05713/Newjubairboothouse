#!/usr/bin/env python3
"""
Jubair Boot House - Startup Script
Run this script to start the FastAPI application
"""

import uvicorn
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

if __name__ == "__main__":
    print("🚀 Starting Jubair Boot House...")
    print("📍 Application will be available at: http://localhost:8000")
    print("🔐 Admin setup: http://localhost:8000/auth/setup")
    print("📚 API docs: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Jubair Boot House...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("💡 Make sure you have:")
        print("   1. Installed requirements: pip install -r requirements.txt")
        print("   2. Set up PostgreSQL and create a database user")
        print("   3. Set DATABASE_URL env var (e.g., postgresql+psycopg2://user:pass@host:5432/db)")
        sys.exit(1)
