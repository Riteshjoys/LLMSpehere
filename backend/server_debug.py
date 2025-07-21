from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize FastAPI app
app = FastAPI(title="ContentForge AI API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers one by one to identify the problematic one
try:
    from modules.auth_routes import auth_router
    app.include_router(auth_router)
    print("✅ Auth router included")
except Exception as e:
    print(f"❌ Auth router failed: {e}")

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Root endpoint
@app.get("/api/")
async def root():
    return {"message": "ContentForge AI API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)