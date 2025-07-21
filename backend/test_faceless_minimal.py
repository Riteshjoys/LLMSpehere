from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize FastAPI app
app = FastAPI(title="Faceless Content Test API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import only the faceless content routes
try:
    from modules.faceless_content_routes import router as faceless_content_router
    app.include_router(faceless_content_router)
    print("✅ Faceless content routes included successfully")
except Exception as e:
    print(f"❌ Failed to include faceless content routes: {e}")

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Root endpoint
@app.get("/api/")
async def root():
    return {"message": "Faceless Content Test API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)