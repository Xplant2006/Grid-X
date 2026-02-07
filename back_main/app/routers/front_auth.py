from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime,timezone
from .. import models, database, schemas

router = APIRouter()
# In app/routers/front_auth.py

@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    
    # 1. Check if email exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # 2. Create User (Using the role from input)
    new_user = models.User(
        email=user.email,
        password=user.password, 
        role=user.role,  # <--- UPDATED HERE
        created_at=datetime.now(timezone.utc)
    )

    # 3. Save
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