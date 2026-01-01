# 🚀 Quick Start Guide - SaaS Monitoring Platform

**Project:** SaaS Log Monitoring Platform  
**Version:** 1.0.0  
**Last Updated:** November 25, 2025

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Starting the Application](#starting-the-application)
3. [Stopping the Application](#stopping-the-application)
4. [Application URLs](#application-urls)
5. [User Authentication](#user-authentication)
6. [Useful Commands](#useful-commands)
7. [Troubleshooting](#troubleshooting)

---

## ✅ Prerequisites

Before starting, ensure you have:

- ✅ **Docker Desktop** installed and running
- ✅ **Docker Compose** installed
- ✅ **PowerShell** or **WSL2** (for Windows users)
- ✅ At least **8GB RAM** available
- ✅ Ports **5000, 5601, 9200, 27017, 6379** are free

---

## 🚀 Starting the Application

### Step 1: Navigate to Project Directory

```powershell
cd \\wsl.localhost\Ubuntu\home\ademm\saas-monitoring-platform
```

Or if using WSL:

```bash
cd /home/ademm/saas-monitoring-platform
```

### Step 2: Start All Services

```powershell
docker-compose up -d
```

**What this does:**
- Starts Elasticsearch (port 9200)
- Starts MongoDB (port 27017)
- Starts Redis (port 6379)
- Starts Logstash (internal)
- Starts Kibana (port 5601)
- Starts Flask Web Application (port 5000)

### Step 3: Wait for Services to be Healthy

```powershell
docker-compose ps
```

**Expected Output:**
All services should show `STATUS: Up X minutes (healthy)`

This takes approximately **1-2 minutes** on first start.

### Step 4: Access the Application

Open your browser and go to:

**🌐 http://localhost:5000/register**

---

## 🛑 Stopping the Application

### Stop All Services (Keep Data)

```powershell
docker-compose stop
```

### Stop and Remove Containers (Keep Data)

```powershell
docker-compose down
```

### Stop and Remove Everything (Including Data)

```powershell
docker-compose down -v
```

⚠️ **Warning:** The `-v` flag deletes all data (logs, users, uploads)!

---

## 🌐 Application URLs

### Main Application

| Service | URL | Description |
|---------|-----|-------------|
| **Registration Page** | http://localhost:5000/register | Create new user account |
| **Login Page** | http://localhost:5000/login | Login to existing account |
| **Dashboard** | http://localhost:5000/ | Main dashboard with KPIs |
| **Log Search** | http://localhost:5000/search | Search and filter logs |
| **File Upload** | http://localhost:5000/upload | Upload CSV/JSON log files |

### Backend Services

| Service | URL | Description |
|---------|-----|-------------|
| **Elasticsearch** | http://localhost:9200 | Search engine (JSON API) |
| **Kibana** | http://localhost:5601 | Elasticsearch UI |
| **MongoDB** | mongodb://localhost:27017 | Database (use MongoDB Compass) |
| **Redis** | redis://localhost:6379 | Cache/Sessions (use Redis CLI) |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| http://localhost:5000/api/health | GET | Health check |
| http://localhost:5000/api/register | POST | Register new user |
| http://localhost:5000/api/login | POST | User login |
| http://localhost:5000/api/logout | POST | User logout |
| http://localhost:5000/api/stats | GET | Dashboard statistics |
| http://localhost:5000/api/search | POST | Search logs |
| http://localhost:5000/api/upload | POST | Upload log file |
| http://localhost:5000/api/uploads | GET | List uploaded files |

---

## 🔐 User Authentication

### First Time Setup

1. **Register a New Account**
   ```
   URL: http://localhost:5000/register
   
   Fields:
   - Username: 3-20 characters (alphanumeric + underscore)
   - Email: Valid email format
   - Password: Minimum 8 characters
   - Confirm Password: Must match password
   ```

2. **After Registration**
   - You'll be automatically logged in
   - Redirected to dashboard: http://localhost:5000/
   - Session lasts 7 days

3. **Login (Subsequent Visits)**
   ```
   URL: http://localhost:5000/login
   
   Fields:
   - Username or Email: Your registration username/email
   - Password: Your password
   - Remember Me: (Optional) Extend session
   ```

4. **Logout**
   - Click "Logout" button in top-right navbar
   - Or go to: http://localhost:5000/api/logout

### Protected Routes

These pages require authentication:

- ✅ `/` - Dashboard
- ✅ `/search` - Log Search
- ✅ `/upload` - File Upload

If not logged in, you'll be redirected to `/login`

---

## 🛠️ Useful Commands

### Check Service Status

```powershell
# View all running containers
docker-compose ps

# Check specific service
docker-compose ps webapp
```

### View Logs

```powershell
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs webapp
docker-compose logs elasticsearch
docker-compose logs mongodb

# Follow logs in real-time
docker-compose logs -f webapp

# View last 50 lines
docker-compose logs --tail=50 webapp
```

### Restart Services

```powershell
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart webapp
```

### Rebuild After Code Changes

```powershell
# Rebuild webapp image
docker-compose build webapp

# Rebuild and restart
docker-compose up -d --build webapp
```

### Access Service Shells

```powershell
# Access Flask app container
docker exec -it saas-webapp sh

# Access MongoDB shell
docker exec -it saas-mongodb mongosh -u admin -p password123

# Access Redis CLI
docker exec -it saas-redis redis-cli

# Access Elasticsearch
docker exec -it saas-elasticsearch bash
```

### Database Operations

```powershell
# MongoDB - View users
docker exec -it saas-mongodb mongosh -u admin -p password123 --eval "use saas_logs; db.users.find().pretty()"

# MongoDB - Count users
docker exec -it saas-mongodb mongosh -u admin -p password123 --eval "use saas_logs; db.users.countDocuments()"

# Redis - View all keys
docker exec -it saas-redis redis-cli KEYS "*"

# Redis - View session
docker exec -it saas-redis redis-cli GET "session:YOUR_SESSION_ID"

# Elasticsearch - Check indices
curl http://localhost:9200/_cat/indices?v

# Elasticsearch - Count logs
curl http://localhost:9200/saas-logs-*/_count
```

### Clean Up

```powershell
# Remove stopped containers
docker-compose down

# Remove all containers and volumes
docker-compose down -v

# Remove unused images
docker image prune -a

# Complete cleanup (use with caution!)
docker system prune -a --volumes
```

---

## 🐛 Troubleshooting

### Problem: Port Already in Use

**Error:** `Bind for 0.0.0.0:5000 failed: port is already allocated`

**Solution:**
```powershell
# Find what's using the port
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
# ports:
#   - "5001:5000"  # Use 5001 instead
```

### Problem: Services Not Healthy

**Error:** Container shows `unhealthy` status

**Solution:**
```powershell
# Check logs for errors
docker-compose logs <service-name>

# Restart the service
docker-compose restart <service-name>

# If still failing, rebuild
docker-compose down
docker-compose up -d --build
```

### Problem: Cannot Connect to MongoDB

**Error:** `MongoServerError: Authentication failed`

**Solution:**
```powershell
# Verify credentials in docker-compose.yml
# Username: admin
# Password: password123

# Reset MongoDB
docker-compose down
docker volume rm saas-monitoring-platform_mongodb-data
docker-compose up -d mongodb
```

### Problem: Elasticsearch Memory Issues

**Error:** `bootstrap checks failed. You must address the points described in the following [1] lines before starting Elasticsearch`

**Solution:**
```powershell
# Increase Docker memory to at least 4GB in Docker Desktop settings

# Or reduce ES memory in docker-compose.yml:
# environment:
#   - "ES_JAVA_OPTS=-Xms256m -Xmx256m"
```

### Problem: 404 Error on /register or /login

**Error:** Page shows "Not Found"

**Solution:**
```powershell
# The webapp needs to be rebuilt to include new routes
docker-compose build webapp
docker-compose up -d webapp

# Wait 5-10 seconds for app to start
docker-compose logs -f webapp
```

### Problem: Session Not Persisting

**Error:** Logged out after refresh

**Solution:**
```powershell
# Check Redis is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Verify session in Redis
docker exec -it saas-redis redis-cli KEYS "session:*"
```

### Problem: Dashboard Shows No Data

**Cause:** No logs in Elasticsearch

**Solution:**
```powershell
# Generate sample logs (if script exists)
python generate_saas_logs.py

# Upload logs via UI
# Go to http://localhost:5000/upload
# Upload saas_logs.csv or saas_logs.json

# Or run Logstash manually
docker-compose restart logstash
```

---

## 📊 Quick Test Workflow

### 1. Start Application
```powershell
docker-compose up -d
```

### 2. Wait for Services
```powershell
# Wait 60 seconds, then check
Start-Sleep -Seconds 60
docker-compose ps
```

### 3. Create Account
- Open: http://localhost:5000/register
- Username: `testuser`
- Email: `test@example.com`
- Password: `password123`
- Submit form

### 4. Verify Dashboard
- Should redirect to: http://localhost:5000/
- Check KPIs load
- Check sparkline charts appear

### 5. Test Logout
- Click "Logout" button
- Should redirect to: http://localhost:5000/login

### 6. Test Login
- Username: `testuser`
- Password: `password123`
- Should redirect to dashboard

### 7. Test Protected Routes
- Open incognito window
- Try accessing: http://localhost:5000/
- Should redirect to login

---

## 🔗 External Tools

### MongoDB GUI

**MongoDB Compass:**
```
Connection String: mongodb://admin:password123@localhost:27017/saas_logs?authSource=admin
```

Download: https://www.mongodb.com/products/compass

### Redis GUI

**Redis Insight:**
```
Host: localhost
Port: 6379
```

Download: https://redis.com/redis-enterprise/redis-insight/

### Elasticsearch GUI

**Kibana:**
```
URL: http://localhost:5601
```

No authentication required (dev mode)

---

## 📝 Environment Variables

Located in `docker-compose.yml`:

```yaml
# Flask App
FLASK_ENV=production
SECRET_KEY=dev-secret-key-change-in-production

# Elasticsearch
ELASTICSEARCH_HOST=http://elasticsearch:9200

# MongoDB
MONGODB_HOST=mongodb
MONGODB_PORT=27017
MONGODB_USER=admin
MONGODB_PASSWORD=password123
MONGODB_DATABASE=saas_logs

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

⚠️ **Change `SECRET_KEY` before production deployment!**

---

## 🎯 Quick Reference Card

### Essential URLs
```
Registration:  http://localhost:5000/register
Login:         http://localhost:5000/login
Dashboard:     http://localhost:5000/
Search:        http://localhost:5000/search
Upload:        http://localhost:5000/upload
Kibana:        http://localhost:5601
```

### Essential Commands
```powershell
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f webapp

# Rebuild
docker-compose build webapp && docker-compose up -d webapp

# Status
docker-compose ps
```

### Default Credentials
```
MongoDB:
  User: admin
  Pass: password123

First User: (create via registration)
  URL: http://localhost:5000/register
```

---

## 📞 Support

**Documentation:**
- `docs/IMPLEMENTATION_SUMMARY.md` - Project overview
- `docs/USER_REGISTRATION_IMPLEMENTATION.md` - Auth system details
- `docs/DASHBOARD_ENHANCEMENT.md` - Dashboard features
- `docs/JIRA_TICKETS.md` - Development roadmap

**Logs Location:**
- Application logs: `docker-compose logs webapp`
- All logs: `docker-compose logs`

**Data Persistence:**
- Elasticsearch: `elasticsearch-data` volume
- MongoDB: `mongodb-data` volume
- Redis: `redis-data` volume

---

**Happy Monitoring! 🎉**

For issues or questions, check the logs or review the documentation files.
