import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Incident, IncidentStatus, IncidentSeverity
from app.core.security import create_access_token


@pytest.fixture
async def auth_headers(test_user):
    """Get authorization headers with valid token."""
    token = create_access_token(data={"sub": str(test_user.id), "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_incident(
    client: AsyncClient,
    test_user,
    auth_headers,
):
    """Test creating a new incident."""
    response = await client.post(
        "/incidents",
        json={
            "title": "Database Connection Timeout",
            "description": "Our application is experiencing database connection timeouts on the production server.",
            "severity": "high",
        },
        headers=auth_headers,
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Database Connection Timeout"
    assert data["severity"] == "high"
    assert data["status"] == "open"
    assert data["created_by"] == test_user.id


@pytest.mark.asyncio
async def test_create_incident_invalid_severity(
    client: AsyncClient,
    auth_headers,
):
    """Test creating incident with invalid severity."""
    response = await client.post(
        "/incidents",
        json={
            "title": "Some Issue",
            "description": "This is a description of the issue.",
            "severity": "invalid_severity",
        },
        headers=auth_headers,
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_incident_short_title(
    client: AsyncClient,
    auth_headers,
):
    """Test creating incident with short title."""
    response = await client.post(
        "/incidents",
        json={
            "title": "Bad",
            "description": "This is a description of the issue.",
            "severity": "medium",
        },
        headers=auth_headers,
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_incident_missing_auth(client: AsyncClient):
    """Test creating incident without authentication."""
    response = await client.post(
        "/incidents",
        json={
            "title": "Some Issue",
            "description": "This is a description of the issue.",
            "severity": "medium",
        },
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_incidents(
    client: AsyncClient,
    test_db: AsyncSession,
    test_user,
    auth_headers,
):
    """Test listing incidents."""
    # Create test incidents
    for i in range(5):
        incident = Incident(
            title=f"Test Incident {i}",
            description=f"Description {i}",
            severity=IncidentSeverity.MEDIUM,
            status=IncidentStatus.OPEN,
            created_by=test_user.id,
        )
        test_db.add(incident)
    
    await test_db.commit()
    
    # List incidents
    response = await client.get(
        "/incidents",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 5
    assert len(data["incidents"]) >= 5


@pytest.mark.asyncio
async def test_list_incidents_with_pagination(
    client: AsyncClient,
    test_db: AsyncSession,
    test_user,
    auth_headers,
):
    """Test listing incidents with pagination."""
    # Create test incidents
    for i in range(10):
        incident = Incident(
            title=f"Test Incident {i}",
            description=f"Description {i}",
            severity=IncidentSeverity.MEDIUM,
            status=IncidentStatus.OPEN,
            created_by=test_user.id,
        )
        test_db.add(incident)
    
    await test_db.commit()
    
    # List with pagination
    response = await client.get(
        "/incidents?skip=0&limit=5",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["incidents"]) == 5


@pytest.mark.asyncio
async def test_list_incidents_filter_by_severity(
    client: AsyncClient,
    test_db: AsyncSession,
    test_user,
    auth_headers,
):
    """Test filtering incidents by severity."""
    # Create incidents with different severities
    for severity in ["low", "medium", "high", "critical"]:
        incident = Incident(
            title=f"Test Incident {severity}",
            description=f"Description {severity}",
            severity=IncidentSeverity(severity),
            status=IncidentStatus.OPEN,
            created_by=test_user.id,
        )
        test_db.add(incident)
    
    await test_db.commit()
    
    # Filter by critical
    response = await client.get(
        "/incidents?severity=critical",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    for incident in data["incidents"]:
        assert incident["severity"] == "critical"


@pytest.mark.asyncio
async def test_get_incident(
    client: AsyncClient,
    test_db: AsyncSession,
    test_user,
    auth_headers,
):
    """Test getting a specific incident."""
    # Create an incident
    incident = Incident(
        title="Test Incident",
        description="This is a test incident",
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.INVESTIGATING,
        created_by=test_user.id,
    )
    test_db.add(incident)
    await test_db.commit()
    await test_db.refresh(incident)
    
    # Get the incident
    response = await client.get(
        f"/incidents/{incident.id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == incident.id
    assert data["title"] == "Test Incident"


@pytest.mark.asyncio
async def test_get_incident_not_found(
    client: AsyncClient,
    auth_headers,
):
    """Test getting non-existent incident."""
    response = await client.get(
        "/incidents/9999",
        headers=auth_headers,
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_incident(
    client: AsyncClient,
    test_db: AsyncSession,
    test_user,
    auth_headers,
):
    """Test updating an incident."""
    # Create an incident
    incident = Incident(
        title="Original Title",
        description="Original description",
        severity=IncidentSeverity.MEDIUM,
        status=IncidentStatus.OPEN,
        created_by=test_user.id,
    )
    test_db.add(incident)
    await test_db.commit()
    await test_db.refresh(incident)
    
    # Update the incident
    response = await client.patch(
        f"/incidents/{incident.id}",
        json={
            "title": "Updated Title",
            "severity": "critical",
            "status": "investigating",
        },
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["severity"] == "critical"
    assert data["status"] == "investigating"


@pytest.mark.asyncio
async def test_update_incident_partial(
    client: AsyncClient,
    test_db: AsyncSession,
    test_user,
    auth_headers,
):
    """Test partial incident update."""
    # Create an incident
    incident = Incident(
        title="Original Title",
        description="Original description",
        severity=IncidentSeverity.MEDIUM,
        status=IncidentStatus.OPEN,
        created_by=test_user.id,
    )
    test_db.add(incident)
    await test_db.commit()
    await test_db.refresh(incident)
    
    # Update only status
    response = await client.patch(
        f"/incidents/{incident.id}",
        json={"status": "resolved"},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Original Title"  # Unchanged
    assert data["status"] == "resolved"


@pytest.mark.asyncio
async def test_delete_incident(
    client: AsyncClient,
    test_db: AsyncSession,
    test_user,
    auth_headers,
):
    """Test deleting an incident."""
    # Create an incident
    incident = Incident(
        title="Test Incident",
        description="This is a test incident",
        severity=IncidentSeverity.LOW,
        status=IncidentStatus.OPEN,
        created_by=test_user.id,
    )
    test_db.add(incident)
    await test_db.commit()
    incident_id = incident.id
    
    # Delete the incident
    response = await client.delete(
        f"/incidents/{incident_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 204
    
    # Verify it's deleted
    response = await client.get(
        f"/incidents/{incident_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_incident_stats(
    client: AsyncClient,
    test_db: AsyncSession,
    test_user,
    auth_headers,
):
    """Test getting incident statistics."""
    # Create incidents with different severities
    for severity in ["critical", "critical", "high", "medium"]:
        incident = Incident(
            title=f"Incident {severity}",
            description="Test",
            severity=IncidentSeverity(severity),
            status=IncidentStatus.OPEN,
            created_by=test_user.id,
        )
        test_db.add(incident)
    
    await test_db.commit()
    
    # Get stats
    response = await client.get(
        "/incidents/stats/overview",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_incidents"] >= 4
    assert data["critical_count"] >= 2