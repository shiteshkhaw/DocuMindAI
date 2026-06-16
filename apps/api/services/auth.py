import uuid
import logging
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from models.auth import UserModel, SessionModel
from schemas.auth import UserCreate, UserLogin, TokenResponse
from config import settings

logger = logging.getLogger("documind.services.auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = getattr(settings, "JWT_SECRET", "super-secret-key-for-dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# Security gate: warn loudly if the default insecure secret is being used in production
_INSECURE_DEFAULTS = {"super-secret-key-for-dev", "", "secret", "changeme"}
if SECRET_KEY.lower() in _INSECURE_DEFAULTS or len(SECRET_KEY) < 32:
    import warnings
    warnings.warn(
        "[AUTH] JWT_SECRET is set to an insecure default or is too short (< 32 chars). "
        "Set a strong random secret in the environment before deploying to production.",
        stacklevel=1
    )

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = (datetime.now(timezone.utc) + expires_delta).replace(tzinfo=None)
        else:
            expire = (datetime.now(timezone.utc) + timedelta(minutes=15)).replace(tzinfo=None)
        to_encode.update({
            "exp": expire,
            "jti": str(uuid.uuid4())
        })
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def signup(self, user_in: UserCreate, generate_token: bool = True) -> UserModel:
        query = select(UserModel).where(UserModel.email == user_in.email)
        result = await self.db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
            
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        user = UserModel(
            id=f"usr-{uuid.uuid4()}",
            email=user_in.email,
            name=user_in.name,
            password_hash=self.get_password_hash(user_in.password),
            auth_provider="local",
            created_at=now,
            updated_at=now
        )
        self.db.add(user)
        
        # Create default workspace
        from models.workspace import WorkspaceModel
        default_workspace = WorkspaceModel(
            id=f"ws-{uuid.uuid4()}",
            user_id=user.id,
            name="Personal Workspace",
            description="Your default workspace",
            created_at=now
        )
        self.db.add(default_workspace)
        
        if generate_token:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": user.id}, expires_delta=access_token_expires
            )
            refresh_token = f"rf-{uuid.uuid4()}"
            
            session = SessionModel(
                id=f"sess-{uuid.uuid4()}",
                user_id=user.id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=(datetime.now(timezone.utc) + timedelta(days=7)).replace(tzinfo=None),
                created_at=now
            )
            self.db.add(session)
            
            # Dynamically attach token details
            user.access_token = access_token
            user.refresh_token = refresh_token
            user.token_type = "bearer"
            user.expires_in = ACCESS_TOKEN_EXPIRE_MINUTES * 60
            
        await self.db.commit()
        return user

    async def login(self, user_in: UserLogin) -> TokenResponse:
        query = select(UserModel).where(UserModel.email == user_in.email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if not user or not self.verify_password(user_in.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
            
        user.last_login_at = datetime.now(timezone.utc).replace(tzinfo=None)

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        refresh_token = f"rf-{uuid.uuid4()}"
        
        session = SessionModel(
            id=f"sess-{uuid.uuid4()}",
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=(datetime.now(timezone.utc) + timedelta(days=7)).replace(tzinfo=None)
        )
        self.db.add(session)
        await self.db.commit()
        
        from schemas.auth import UserResponse
        user_res = UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_res
        )

    async def google_login(self, token: str) -> TokenResponse:
        try:
            # The token from useGoogleLogin (implicit flow) is an access token
            import requests
            response = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code != 200:
                raise ValueError("Invalid token")
            idinfo = response.json()
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid Google token")

        email = idinfo.get("email")
        google_id = idinfo.get("sub")
        name = idinfo.get("name", "Google User")

        if not email or not google_id:
            raise HTTPException(status_code=400, detail="Missing required info from Google")

        # Check if user exists by email
        query = select(UserModel).where(UserModel.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if user:
            # Link google_id if not linked
            if not user.google_id:
                user.google_id = google_id
                if user.auth_provider == "local":
                    user.auth_provider = "local_google"
            user.last_login_at = now
        else:
            # Auto-provision user
            user = UserModel(
                id=f"usr-{uuid.uuid4()}",
                email=email,
                name=name,
                password_hash=None,
                google_id=google_id,
                auth_provider="google",
                created_at=now,
                updated_at=now
            )
            self.db.add(user)

            # Create default workspace
            from models.workspace import WorkspaceModel
            default_workspace = WorkspaceModel(
                id=f"ws-{uuid.uuid4()}",
                user_id=user.id,
                name="Personal Workspace",
                description="Your default workspace",
                created_at=now
            )
            self.db.add(default_workspace)

        # Generate session identical to local login
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        refresh_token = f"rf-{uuid.uuid4()}"

        session = SessionModel(
            id=f"sess-{uuid.uuid4()}",
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=(datetime.now(timezone.utc) + timedelta(days=7)).replace(tzinfo=None),
            created_at=now
        )
        self.db.add(session)
        await self.db.commit()

        from schemas.auth import UserResponse
        user_res = UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_res
        )
        
    async def logout(self, access_token: str):
        query = select(SessionModel).where(SessionModel.access_token == access_token)
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        if session:
            await self.db.delete(session)
            await self.db.commit()

    async def get_current_user(self, token: str) -> UserModel:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if not user_id or not isinstance(user_id, str):
                raise HTTPException(status_code=401, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        return user
