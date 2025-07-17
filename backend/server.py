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
from modules.social_media_routes import social_media_router
from modules.workflow_routes import router as workflow_router
from modules.workflow_scheduler_routes import router as scheduler_router
from modules.workflow_monitoring_routes import router as monitoring_router
from modules.dashboard_routes import router as dashboard_router
from modules.admin_api_keys_routes import router as admin_api_keys_router
from modules.user_routes import router as user_router
from modules.analytics_routes import router as analytics_router
from modules.presentation_routes import router as presentation_router
from modules.viral_content_routes import router as viral_content_router
from modules.startup import initialize_default_data, shutdown_scheduler

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
app.include_router(code_router)
app.include_router(social_media_router)
app.include_router(workflow_router)
app.include_router(scheduler_router)
app.include_router(monitoring_router)
app.include_router(dashboard_router)
app.include_router(admin_api_keys_router)
app.include_router(user_router)
app.include_router(analytics_router)
app.include_router(presentation_router)
app.include_router(viral_content_router)

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

# Shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    await shutdown_scheduler()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)