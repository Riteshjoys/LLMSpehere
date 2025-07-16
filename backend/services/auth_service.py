import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException
from models.user_models import UserCreate, UserLogin, UserResponse
from utils.auth_utils import create_access_token, verify_password, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from utils.database import users_collection

class AuthService:
    @staticmethod
    async def register_user(user_data: UserCreate):
        """Register a new user"""
        # Check if user exists
        if users_collection.find_one({"username": user_data.username}):
            raise HTTPException(status_code=400, detail="Username already registered")
        
        if users_collection.find_one({"email": user_data.email}):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        user_doc = {
            "user_id": str(uuid.uuid4()),
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "is_admin": False,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        users_collection.insert_one(user_doc)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    @staticmethod
    async def login_user(user_data: UserLogin):
        """Login user and return access token"""
        user_doc = users_collection.find_one({"username": user_data.username})
        
        if not user_doc or not verify_password(user_data.password, user_doc["hashed_password"]):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    @staticmethod
    async def get_current_user_info(username: str) -> UserResponse:
        """Get current user information"""
        user_doc = users_collection.find_one({"username": username})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get usage stats for the user
        from services.user_service import UserService
        try:
            usage_stats = await UserService.get_user_usage_stats(user_doc["user_id"])
            usage_stats_dict = usage_stats.dict()
        except:
            usage_stats_dict = None
        
        return UserResponse(
            user_id=user_doc["user_id"],
            username=user_doc["username"],
            email=user_doc["email"],
            is_admin=user_doc.get("is_admin", False),
            created_at=user_doc["created_at"],
            profile=user_doc.get("profile", {}),
            preferences=user_doc.get("preferences", {}),
            plan=user_doc.get("plan", "free"),
            role=user_doc.get("role", "user"),
            last_login=user_doc.get("last_login"),
            usage_stats=usage_stats_dict
        )
    
    @staticmethod
    def is_admin(username: str) -> bool:
        """Check if user is admin"""
        user_doc = users_collection.find_one({"username": username})
        return user_doc.get("is_admin", False) if user_doc else False