from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from schemas.auth import UserCreate, UserLogin, TokenResponse, UserResponse, GoogleLogin
from services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.get_current_user(token)

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.signup(user_in)
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

@router.post("/login", response_model=TokenResponse)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.login(user_in)

@router.post("/google", response_model=TokenResponse)
async def google_login(google_in: GoogleLogin, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.google_login(google_in.token)

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.logout(token)
    return {"success": True}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
