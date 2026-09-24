import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient

from app.core import Base, get_settings
from app.main import app
from app.db.models import User, UserRole
from app.core.security import hash_password


# Override database URL for testing
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    settings = get_settings()
    engine = create_async_engine(
        settings.database_test_url,
        echo=False,
        future=True,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(test_engine):
    """Create test client with overridden database dependency."""
    from app.core import get_db
    
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async def override_get_db():
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        role=UserRole.ENGINEER,
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def test_admin(test_db: AsyncSession) -> User:
    """Create a test admin user."""
    admin = User(
        username="testadmin",
        email="admin@example.com",
        password_hash=hash_password("adminpass123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    test_db.add(admin)
    await test_db.commit()
    await test_db.refresh(admin)
    return admin


@pytest.fixture
def test_user_credentials():
    """Provide test user credentials."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
    }


@pytest.fixture
def test_admin_credentials():
    """Provide test admin credentials."""
    return {
        "username": "testadmin",
        "email": "admin@example.com",
        "password": "adminpass123",
    }