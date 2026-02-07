from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from .. import models, database, schemas

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    
    # 1. Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # 2. Create the new User (PLAIN TEXT PASSWORD)
    new_user = models.User(
        email=user.email,
        password=user.password,  # Stored directly as plain text
        role="buyer",            # Default role
        created_at=datetime.timezone.utc.now()
    )

    # 3. Save to Database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# In routers/front_auth.py

@router.post("/login", response_model=schemas.UserResponse)
def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    
    # 1. Find user by email
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    # 2. Check if user exists
    if not user:
        # Security Tip: Generic message prevents hackers from guessing emails
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # 3. Check if password matches (Plain Text comparison)
    if user.password != user_credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # 4. Success! Return the user data
    return user