from fastapi import APIRouter, Depends
from models.user_models import UserCreate, UserLogin, UserResponse
from services.auth_service import AuthService
from utils.auth_utils import get_current_user

auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@auth_router.post("/register")
async def register(user: UserCreate):
    """Register a new user"""
    return await AuthService.register_user(user)

@auth_router.post("/login")
async def login(user: UserLogin):
    """Login user"""
    return await AuthService.login_user(user)

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """Get current user information"""
    return await AuthService.get_current_user_info(current_user)