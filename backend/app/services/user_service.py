from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, UserRole
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.users import UserRegister, UserResponse, TokenResponse


class UserService:
    """Service for user management operations."""
    
    @staticmethod
    async def create_user(
        session: AsyncSession,
        user_data: UserRegister,
    ) -> User:
        """Create a new user."""
        # Check if user already exists
        stmt = select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
        existing_user = await session.execute(stmt)
        if existing_user.scalar_one_or_none():
            raise ValueError("User with this email or username already exists")
        
        # Create new user
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            role=UserRole.ENGINEER,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    
    @staticmethod
    async def authenticate_user(
        session: AsyncSession,
        email: str,
        password: str,
    ) -> User | None:
        """Authenticate user by email and password."""
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    async def get_user_by_id(
        session: AsyncSession,
        user_id: int,
    ) -> User | None:
        """Get user by ID."""
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(
        session: AsyncSession,
        email: str,
    ) -> User | None:
        """Get user by email."""
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    def create_token_response(user: User) -> TokenResponse:
        """Create token response for authenticated user."""
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )