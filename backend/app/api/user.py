from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.oauth2 import get_current_user
from app.models.user import User

from app.database.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone": current_user.phone,
        "location": current_user.location
    }