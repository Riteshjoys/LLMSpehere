from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.auth_routes import auth_router
from modules.provider_routes import provider_router
from modules.generation_routes import generation_router
from modules.code_generation_routes import router as code_router
from modules.startup import initialize_default_data

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

# Include routers
app.include_router(auth_router)
app.include_router(provider_router)
app.include_router(generation_router)

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Root endpoint
@app.get("/api/")
async def root():
    return {"message": "ContentForge AI API", "version": "1.0.0"}

# Initialize default providers and admin user
@app.on_event("startup")
async def startup_event():
    """Initialize default providers and admin user if they don't exist"""
    await initialize_default_data()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)