# API Server Errors Troubleshooting Guide

## Issue: 500 Internal Server Error

### Symptoms
- FastAPI returns 500 status code
- No error details in response
- Application is running but responding with errors

### Root Causes
1. Unhandled exception in code
2. Database connection lost
3. Invalid request processing
4. Missing environment variables

### Resolution Steps

#### Step 1: Check Application Logs
```bash
# For Docker container
docker-compose logs -f backend

# For local development
# Check terminal where uvicorn is running

# Look for stack traces and error messages
```

#### Step 2: Review Recent Code Changes
```bash
git log --oneline -10
git diff HEAD~1
```

#### Step 3: Verify Environment Variables
```bash
# Check .env file exists and is correct
cat .env

# Ensure all required variables are set
printenv | grep DATABASE_URL
printenv | grep SECRET_KEY
```

#### Step 4: Test with Swagger UI
- Navigate to http://localhost:8000/docs
- Use "Try it out" to test endpoints
- Check request/response in browser console

#### Step 5: Enable Debug Logging
```python
# In config.py
LOG_LEVEL = "DEBUG"

# In docker-compose.yml
DEBUG: "true"
```

### Prevention
- Add comprehensive error logging
- Use try-catch with specific exception handling
- Validate all inputs with Pydantic
- Test edge cases and error conditions
- Use environment variable validation at startup

---

## Issue: 401 Unauthorized / Invalid Token

### Symptoms
- Requests return 401 Unauthorized
- "Invalid token" or "Token expired" messages
- Headers missing Bearer token

### Root Causes
1. Missing Authorization header
2. Malformed token
3. Token expired
4. Wrong secret key used for validation
5. Token algorithm mismatch

### Resolution Steps

#### Step 1: Verify Token Format
```bash
# Correct format
Authorization: Bearer <token>

# Common mistakes
- Missing "Bearer " prefix
- Extra spaces
- Typos in token
```

#### Step 2: Check Token Content
```python
# Decode token manually (for debugging only)
from jose import jwt
from app.core.config import get_settings

settings = get_settings()
payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
print(payload)
```

#### Step 3: Verify Secret Key
```bash
# Ensure SECRET_KEY is same across all instances
echo $SECRET_KEY
wc -c <<< $SECRET_KEY  # Should be 32+ characters
```

#### Step 4: Check Token Expiration
```python
from datetime import datetime, timezone
import jwt

payload = jwt.decode(token, key, algorithms=["HS256"])
exp = payload.get("exp")
now = datetime.now(timezone.utc).timestamp()
print(f"Expired: {exp < now}")
```

### Prevention
- Store SECRET_KEY securely, never in code
- Implement token refresh mechanism
- Log token validation failures
- Set reasonable expiration times
- Use HTTPS in production

---

## Issue: 422 Unprocessable Entity

### Symptoms
- Request validation fails
- Pydantic validation errors
- Missing required fields

### Root Causes
1. Missing required request body fields
2. Wrong data types
3. Invalid enum values
4. Constraint violations (min/max length)

### Resolution Steps

#### Step 1: Check Request Body Schema
```python
# Review Pydantic model in schemas/
class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=5)
    description: str
    severity: str
```

#### Step 2: Verify Data Types
```bash
# JSON data types must match schema
- "title": "string"  # Correct
- "title": 123       # Wrong - should be string
- "created_at": "2024-01-01T00:00:00"  # For datetime
```

#### Step 3: Check Enum Values
```python
# Severity must be one of these
severity: "low" | "medium" | "high" | "critical"

# Invalid examples
severity: "LOW"      # Case sensitive
severity: "urgent"   # Not in enum
```

#### Step 4: Review Error Details
- Look at 422 response body for detailed validation errors
- Each field shows what constraint was violated
- Use Swagger UI to test and validate payload

### Prevention
- Use Pydantic models for all request validation
- Add detailed error messages in models
- Document API schemas thoroughly
- Test with multiple client libraries

---

## Issue: 503 Service Unavailable

### Symptoms
- Cannot reach API at all
- Connection refused
- Service not responding

### Root Causes
1. FastAPI not running
2. Port not exposed correctly
3. Container not started
4. Network issues
5. Resource exhaustion

### Resolution Steps

#### Step 1: Check Container Status
```bash
docker-compose ps
# STATUS should be "Up"

docker-compose logs backend
# Look for startup errors
```

#### Step 2: Test Port Connectivity
```bash
# Check if port is listening
netstat -tulpn | grep 8000

# Test with curl
curl -v http://localhost:8000/health

# For Docker containers
docker exec incident-backend curl localhost:8000/health
```

#### Step 3: Restart Service
```bash
# Restart specific service
docker-compose restart backend

# Or full restart
docker-compose down
docker-compose up -d backend
```

#### Step 4: Check Resource Usage
```bash
# CPU and memory
docker stats incident-backend

# Disk space
df -h

# Container logs for crashes
docker-compose logs --tail=50 backend
```

### Prevention
- Implement health checks
- Monitor resource usage
- Set resource limits
- Use container restart policies
- Regular backup and recovery testing

---

## Debug Checklist

- [ ] Check application logs
- [ ] Verify environment variables
- [ ] Confirm database connectivity
- [ ] Validate JWT tokens
- [ ] Check request/response format
- [ ] Review recent code changes
- [ ] Test with Swagger UI
- [ ] Check Docker container status
- [ ] Monitor system resources
- [ ] Review firewall rules

## Quick Commands

```bash
# Get backend logs
docker-compose logs -f backend

# Test health endpoint
curl http://localhost:8000/health

# Check all services
docker-compose ps

# Restart backend
docker-compose restart backend

# View API docs
curl -s http://localhost:8000/openapi.json | jq .

# Test with httpx
python -c "
import httpx
client = httpx.Client(base_url='http://localhost:8000')
print(client.get('/health').json())
"
```

## Getting Help

Include when reporting issues:
1. Full error message and stack trace
2. Request details (method, URL, headers, body)
3. Response status and body
4. Docker Compose logs (sanitize credentials)
5. Environment configuration
6. Steps to reproduce