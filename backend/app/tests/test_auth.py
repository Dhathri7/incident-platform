import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    response = await client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "newuser"
    assert data["user"]["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_register_user_invalid_email(client: AsyncClient):
    """Test registration with invalid email."""
    response = await client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "invalid-email",
            "password": "securepassword123",
        },
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_user_short_password(client: AsyncClient):
    """Test registration with too short password."""
    response = await client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "short",
        },
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_user_duplicate_email(client: AsyncClient, test_user):
    """Test registration with existing email."""
    response = await client.post(
        "/auth/register",
        json={
            "username": "differentuser",
            "email": test_user.email,
            "password": "securepassword123",
        },
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_user_duplicate_username(client: AsyncClient, test_user):
    """Test registration with existing username."""
    response = await client.post(
        "/auth/register",
        json={
            "username": test_user.username,
            "email": "different@example.com",
            "password": "securepassword123",
        },
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_valid_credentials(client: AsyncClient, test_user, test_user_credentials):
    """Test login with valid credentials."""
    response = await client.post(
        "/auth/login",
        json={
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"],
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["id"] == test_user.id


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user):
    """Test login with invalid password."""
    response = await client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword",
        },
    )
    
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent email."""
    response = await client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "anypassword",
        },
    )
    
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_verify_token(client: AsyncClient, test_user, test_user_credentials):
    """Test token verification."""
    # First login to get token
    login_response = await client.post(
        "/auth/login",
        json={
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"],
        },
    )
    
    token = login_response.json()["access_token"]
    
    # Verify token
    response = await client.post(
        "/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_verify_token_invalid(client: AsyncClient):
    """Test verification with invalid token."""
    response = await client.post(
        "/auth/verify",
        headers={"Authorization": "Bearer invalid-token"},
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_verify_token_missing_header(client: AsyncClient):
    """Test verification without authorization header."""
    response = await client.post(
        "/auth/verify",
    )
    
    assert response.status_code == 401