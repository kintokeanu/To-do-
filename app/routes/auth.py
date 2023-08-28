from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ..schemas.user import User, UserCreate,UserInDB
from ..database import database
from ..config import settings
import jwt
import bcrypt


router = APIRouter(
    prefix='/users',
    tags=['Users']
)

# User registration endpoint
@router.post("/login", response_model=User)
async def register_user(user_data: UserCreate):
    # Check if user with email already exists
    existing_user = await database.client[settings.MONGODB_NAME].users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password before saving
    hashed_password = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt())
    new_user = {"username": user_data.username, "email": user_data.email, "hashed_password": hashed_password.decode()}
    
    result = await database.client[settings.MONGODB_NAME].users.insert_one(new_user)
    new_user["id"] = str(result.inserted_id)
    return new_user

# Token generation endpoint
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Validate user credentials
    user = await database.client[settings.MONGODB_NAME].users.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Verify password
    if not bcrypt.checkpw(form_data.password.encode(), user["hashed_password"].encode()):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Generate JWT token
    token_data = {"sub": user["email"], "exp": timedelta(minutes=settings.access_token_expire_minutes)}
    token = jwt.encode(token_data, settings.secret_key, algorithm="HS256")

    return {"access_token": token, "token_type": "bearer"}