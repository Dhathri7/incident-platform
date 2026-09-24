# Database Connectivity Troubleshooting Guide

## Issue: Cannot Connect to PostgreSQL Database

### Symptoms
- Connection timeout errors
- "psycopg2.OperationalError: could not translate host name"
- Application cannot reach database on port 5432

### Root Causes
1. PostgreSQL service not running
2. Network connectivity issues
3. Incorrect connection string
4. Firewall blocking port 5432
5. Wrong credentials

### Resolution Steps

#### Step 1: Verify PostgreSQL is Running
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if stopped
sudo systemctl start postgresql

# For Docker containers
docker ps | grep postgres
docker-compose ps postgres
```

#### Step 2: Check Network Connectivity
```bash
# Test connection to database host
telnet localhost 5432

# Check if port is listening
netstat -tulpn | grep 5432

# For Docker networks
docker network ls
docker network inspect incident-network
```

#### Step 3: Verify Connection String
- Format: `postgresql://user:password@host:port/database`
- Example: `postgresql://incident_user:incident_password@postgres:5432/incident_db`
- For async: `postgresql+asyncpg://user:password@host:port/database`

#### Step 4: Check Credentials
```bash
# Test connection with psql
psql -U incident_user -d incident_db -h localhost -W

# Inside Docker container
docker exec incident-postgres psql -U incident_user -d incident_db -c "SELECT 1;"
```

#### Step 5: Review Firewall Rules
```bash
# Check firewall status
sudo ufw status

# Allow PostgreSQL port
sudo ufw allow 5432/tcp
```

### Prevention
- Use environment variables for connection strings
- Implement connection pooling
- Add health checks to services
- Monitor PostgreSQL logs
- Regular backup testing

### Related Issues
- [Connection Pool Exhaustion](#connection-pool-exhaustion)
- [Authentication Failures](#authentication-failures)
- [Slow Query Performance](#slow-query-performance)

---

## Issue: Connection Pool Exhaustion

### Symptoms
- "too many connections" error
- Application hangs when attempting database queries
- Intermittent connection failures under load

### Root Causes
1. Not closing database connections
2. Connection pool size too small
3. Long-running queries holding connections
4. Connection leak in application code

### Resolution Steps

#### Step 1: Check Current Connections
```sql
SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;
SELECT * FROM pg_stat_activity WHERE state != 'idle';
```

#### Step 2: Increase Pool Size
```python
# In config.py
engine = create_async_engine(
    database_url,
    pool_size=20,      # Increase if needed
    max_overflow=10,   # Overflow connections
    pool_pre_ping=True # Validate connections
)
```

#### Step 3: Implement Proper Connection Management
```python
# Always use async context managers
async with AsyncSessionLocal() as session:
    result = await session.execute(query)
    # Connection returned automatically

# Never leave connections open
```

#### Step 4: Monitor and Profile
- Enable slow query logging
- Monitor active connections
- Profile application code for leaks

### Prevention
- Use connection pooling with appropriate sizes
- Implement timeouts on queries
- Regular monitoring and alerting
- Code review for connection management

---

## Issue: Authentication Failures

### Symptoms
- "FATAL: password authentication failed"
- "role does not exist"
- Permission denied errors

### Resolution
1. Verify username and password in connection string
2. Check database role exists: `\du` in psql
3. Reset password: `ALTER USER username WITH PASSWORD 'newpass';`
4. Check pg_hba.conf for authentication methods

### Common Mistakes
- Typos in credentials
- Expired passwords
- Case-sensitive usernames
- Special characters in passwords (needs URL encoding)

---

## Quick Reference

| Issue | Solution |
|-------|----------|
| Port in use | `lsof -i :5432` then kill process |
| Can't connect | Check host/port/credentials |
| Too many connections | Increase pool_size in config |
| Slow queries | Enable slow_query_log, add indexes |
| Disk full | Check with `df -h`, archive old logs |

## Escalation

If issues persist:
1. Check PostgreSQL logs: `/var/log/postgresql/`
2. Enable debug logging in application
3. Contact database administrator
4. Review Docker volumes and disk space