from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.core.security import get_current_user_id
from app.schemas.users import UserRegister, UserLogin, TokenResponse, UserResponse
from app.services.user_service import UserService
from app.services.audit_service import AuditService

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    responses={
        201: {"description": "User successfully registered"},
        400: {"description": "User already exists"},
    },
)
async def register(
    user_data: UserRegister,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Register a new user.
    
    - **username**: Unique username (3-100 characters)
    - **email**: Valid email address
    - **password**: Password (minimum 8 characters)
    
    Returns access token and user information.
    """
    try:
        # Create user
        user = await UserService.create_user(session, user_data)
        
        # Log action
        await AuditService.log_action(
            session=session,
            user_id=user.id,
            action="USER_REGISTERED",
            resource="user",
            resource_id=user.id,
            details={"email": user.email, "username": user.username},
        )
        
        # Return token
        return UserService.create_token_response(user)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Login with email and password.
    
    - **email**: User email
    - **password**: User password
    
    Returns access token and user information.
    """
    # Authenticate user
    user = await UserService.authenticate_user(
        session=session,
        email=credentials.email,
        password=credentials.password,
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Log action
    await AuditService.log_action(
        session=session,
        user_id=user.id,
        action="USER_LOGIN",
        resource="user",
        resource_id=user.id,
    )
    
    # Return token
    return UserService.create_token_response(user)


@router.post(
    "/verify",
    response_model=UserResponse,
    summary="Verify current access token",
    responses={
        200: {"description": "Token is valid"},
        401: {"description": "Invalid or expired token"},
    },
)
async def verify_token(
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Verify the current access token is valid.
    
    Returns current user information if token is valid.
    """
    user = await UserService.get_user_by_id(session, current_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserResponse.model_validate(user)


# Dependency to extract and validate JWT token
async def get_current_user_id(session: AsyncSession = Depends(get_db)) -> int:
    """Extract user ID from JWT token in Authorization header."""
    from fastapi import Header
    from app.core.security import decode_token
    
    async def _get_current_user(
        authorization: str | None = Header(None),
    ) -> int:
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        payload = decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            return int(user_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    return await _get_current_user()