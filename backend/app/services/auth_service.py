from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.auth.hashing import verify_password
from app.auth.token import create_access_token


def login_user(db: Session, email: str, password: str):
    """
    Authenticate user and generate JWT token.
    """

    # Find user by email
    user = db.query(User).filter(User.email == email).first()

    # Check if user exists
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Generate JWT Token
    access_token = create_access_token(
        data={"sub": user.email}
    )

    # Return token
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }