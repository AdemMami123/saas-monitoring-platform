# 📊 SaaS Monitoring Platform

A production-ready **real-time log monitoring and analytics platform** built with the **ELK Stack** (Elasticsearch, Logstash, Kibana), **Flask**, **MongoDB**, and **Redis**. This platform enables organizations to collect, process, analyze, and visualize application logs in real-time.

**Version:** 1.0.0  
**Last Updated:** January 2026

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Development Guide](#development-guide)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🎯 Overview

The **SaaS Monitoring Platform** is a comprehensive log management solution designed for DevOps engineers and system administrators. It provides:

- **Real-time log ingestion** from multiple sources (CSV, JSON)
- **Advanced search and filtering** capabilities
- **Interactive dashboards** with key performance indicators (KPIs)
- **Data visualization** through Kibana
- **User authentication** with secure password hashing
- **Multi-tenant support** with tenant isolation
- **Scalable architecture** with microservices

**Use Cases:**
- Monitor application performance metrics
- Troubleshoot production issues
- Track API response times and error rates
- Analyze user behavior and system health
- Comply with audit logging requirements

---

## ✨ Features

### 1. **User Authentication & Authorization**
- User registration with email validation
- Secure login with bcrypt password hashing
- Session management with 7-day expiration
- Protected routes and API endpoints
- MongoDB-backed user management

### 2. **File Upload System**
- Support for CSV and JSON log formats
- Drag-and-drop file upload interface
- Automatic file validation
- Metadata tracking (filename, size, timestamp)
- File deletion capability

### 3. **Real-Time Log Processing**
- Logstash pipeline for ETL operations
- CSV and JSON codec support
- Automatic field parsing and type conversion
- GeoIP enrichment for client IPs
- Batch processing for high-volume data

### 4. **Advanced Search & Filtering**
- Full-text search across log messages
- Filter by log level (INFO, WARNING, ERROR, DEBUG, CRITICAL)
- Date range filtering
- Endpoint-based filtering
- HTTP status code filtering (2xx, 4xx, 5xx)
- Server and tenant filtering
- Pagination support (50 results per page)
- Export results to CSV

### 5. **Interactive Dashboard**
- **9 Key Performance Indicators (KPIs):**
  1. Total logs (all-time)
  2. Total logs (last 24 hours)
  3. Error rate (percentage)
  4. Average response time
  5. Top 3 slowest endpoints
  6. Active users (last 24 hours)
  7. Latest error message
  8. Total files uploaded
  9. System health status

- Auto-refresh every 30 seconds
- Real-time sparklines showing trends
- Color-coded health indicators
- Redis caching for performance

### 6. **Data Visualization**
- Kibana integration for advanced analytics
- Pre-configured visualizations:
  - Response time trends (line chart)
  - Status code distribution (pie chart)
  - Top endpoints (bar chart)
  - Error rate timeline
  - Database query performance
- Custom dashboard support

### 7. **Log Generation**
- Faker-based realistic log generation
- 10,000+ sample logs per generation
- Multiple log types (web_request, database_query)
- Configurable time ranges
- Statistical distributions for realistic data

---

## 🏗️ Architecture

### Microservices Architecture (6 Containers)

```
┌─────────────────────────────────────────────────────────┐
│                    Flask Web App (Port 5000)            │
│         (Authentication, API, Upload, Dashboard)        │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┼────────┐
        │        │        │
   ┌────▼──┐ ┌──▼───┐ ┌─▼────┐
   │MongoDB│ │Redis │ │Files │
   │       │ │      │ │      │
   └───────┘ └──────┘ └──┬───┘
                         │
                    ┌────▼────┐
                    │Logstash │ (ETL Pipeline)
                    │         │
                    └────┬────┘
                         │
              ┌──────────▼──────────┐
              │  Elasticsearch     │ (Search & Index)
              │  (Port 9200)       │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │     Kibana        │ (Visualization)
              │    (Port 5601)    │
              └───────────────────┘
```

### Data Flow

```
1. Log Generation (Python Script)
   ↓
2. User Upload via Web UI
   ↓
3. Flask File Processing
   ├─ Save to app/uploads/
   └─ Copy to uploads/ (Logstash input)
   ↓
4. Logstash Processing
   ├─ Parse CSV/JSON
   ├─ Extract & transform fields
   ├─ Add GeoIP data
   └─ Send to Elasticsearch
   ↓
5. Elasticsearch Indexing
   ├─ Create saas-logs-YYYY.MM.dd index
   ├─ Store documents
   └─ Enable search
   ↓
6. Search & Visualization
   ├─ Flask API queries Elasticsearch
   ├─ Kibana creates visualizations
   └─ Redis caches dashboard stats
```

---

## 🛠️ Tech Stack

### Backend
- **Python 3.x** - Server-side language
- **Flask** - Lightweight web framework
- **Gunicorn** - Production WSGI server
- **Elasticsearch** - Search and analytics engine
- **Logstash** - Log processing and transformation
- **MongoDB** - NoSQL database for metadata
- **Redis** - In-memory cache and session store

### Frontend
- **HTML5/CSS3/JavaScript** - Web interface
- **Bootstrap 5** - Responsive UI framework
- **Chart.js** - Interactive dashboard charts
- **Fetch API** - AJAX communication

### Security
- **bcrypt** - Password hashing
- **Flask Sessions** - User authentication
- **CORS** - Cross-origin protection

### DevOps
- **Docker** - Container platform
- **Docker Compose** - Multi-container orchestration

### Development Tools
- **Faker** - Test data generation
- **Python Requests** - HTTP client
- **python-dotenv** - Environment configuration

---

## ✅ Prerequisites

Before installing, ensure you have:

| Requirement | Version | Notes |
|------------|---------|-------|
| **Docker Desktop** | 20.10+ | [Download](https://www.docker.com/products/docker-desktop) |
| **Docker Compose** | 1.29+ | Included with Docker Desktop |
| **Python** | 3.8+ | Only needed for local development |
| **RAM** | 8GB+ | Minimum for all services |
| **Disk Space** | 10GB+ | For containers and data |
| **Available Ports** | 5000, 5601, 9200, 27017, 6379 | Must be free |

### Supported Operating Systems
- ✅ Ubuntu/Debian (Linux)
- ✅ macOS (Intel & Apple Silicon)
- ✅ Windows 10/11 with WSL2
- ✅ Docker Desktop on Windows/Mac

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/saas-monitoring-platform.git
cd saas-monitoring-platform
```

### 2. Configure Environment Variables (Optional)

Create a `.env` file in the project root:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-change-in-production

# MongoDB
MONGODB_HOST=mongodb
MONGODB_PORT=27017
MONGODB_USER=admin
MONGODB_PASSWORD=password123
MONGODB_DATABASE=saas_logs

# Elasticsearch
ELASTICSEARCH_HOST=http://elasticsearch:9200

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Logstash
LOGSTASH_HOST=logstash
```

### 3. Build and Start Services

```bash
# Start all services
docker-compose up -d

# Wait for services to be healthy (1-2 minutes)
docker-compose ps

# All services should show "healthy" status
```

### 4. Verify Installation

```bash
# Check Elasticsearch
curl http://localhost:9200/_cluster/health

# Check MongoDB
docker exec -it saas-mongodb mongosh -u admin -p password123 --eval "db.adminCommand('ping')"

# Check Redis
docker exec -it saas-redis redis-cli ping

# View Flask logs
docker-compose logs -f saas-webapp
```

---

## ⚙️ Configuration

### Docker Compose Services

Edit `docker-compose.yml` to customize:

```yaml
# Flask Web Application
saas-webapp:
  ports:
    - "5000:5000"  # Change port if needed
  environment:
    - FLASK_ENV=production

# Elasticsearch
elasticsearch:
  environment:
    - ES_JAVA_OPTS=-Xms512m -Xmx512m  # Adjust memory as needed
  ports:
    - "9200:9200"

# MongoDB
mongodb:
  environment:
    - MONGO_INITDB_ROOT_USERNAME=admin
    - MONGO_INITDB_ROOT_PASSWORD=password123
  ports:
    - "27017:27017"

# Redis
redis:
  ports:
    - "6379:6379"

# Kibana
kibana:
  ports:
    - "5601:5601"
```

### Flask Configuration

Edit `app/app.py` for application settings:

```python
# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# File upload
app.config['UPLOAD_FOLDER'] = 'app/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

# Redis caching
app.config['CACHE_TIMEOUT'] = 30  # seconds
```

### Logstash Configuration

Edit `logstash/pipeline/logstash.conf` for input/output:

```conf
input {
  file {
    path => "/data/uploads/*"
    start_position => "beginning"
    sincedb_path => "/usr/share/logstash/data/plugins/inputs/file/.sincedb"
    codec => "json"  # or "csv"
  }
}

filter {
  # Add your filters here
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "saas-logs-%{+YYYY.MM.dd}"
  }
}
```

---

## 📁 Project Structure

```
saas-monitoring-platform/
├── app/                              # Flask application
│   ├── app.py                        # Main application (1353 lines)
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Flask container definition
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py                  # User authentication model
│   ├── templates/                    # HTML templates
│   │   ├── index.html               # Dashboard page
│   │   ├── login.html               # Login page
│   │   ├── register.html            # Registration page
│   │   ├── search.html              # Search interface
│   │   └── upload.html              # File upload page
│   └── uploads/                      # User uploaded files
│       └── [timestamp]_[filename]   # Uploaded CSV/JSON files
│
├── logstash/                         # Log processing
│   └── pipeline/
│       └── logstash.conf            # Logstash pipeline config
│
├── uploads/                          # Logstash input folder
│   └── [timestamp]_[filename]       # Files for processing
│
├── docs/                             # Documentation
│   ├── IMPLEMENTATION_SUMMARY.md     # Technical overview
│   ├── USER_REGISTRATION_IMPLEMENTATION.md
│   ├── DASHBOARD_ENHANCEMENT.md
│   ├── KIBANA_SETUP.md
│   ├── SEARCH_FUNCTIONALITY.md
│   ├── UPLOAD_FUNCTIONALITY.md
│   ├── GENERATE_LOGS_GUIDE.md
│   └── kibana_dashboard.json         # Pre-configured dashboard
│
├── generate_logs.py                  # Test data generator (basic)
├── generate_saas_logs.py             # Test data generator (advanced)
├── docker-compose.yml                # Multi-container definition
├── QUICK_START.md                    # Quick reference guide
├── QUICK_REFERENCE.md                # Command cheat sheet
├── README.md                         # This file
└── .gitignore                        # Git ignore rules
```

---

## 🚀 Running the Application

### Start Services

```bash
# Start all services in background
docker-compose up -d

# Wait for health checks (1-2 minutes)
docker-compose ps

# View real-time logs
docker-compose logs -f saas-webapp
```

### First Time Setup

1. **Create User Account**
   ```
   URL: http://localhost:5000/register
   
   Form:
   - Username: 3-20 characters (alphanumeric + underscore)
   - Email: Valid email address
   - Password: Minimum 8 characters
   - Confirm Password: Must match
   ```

2. **Generate Sample Logs** (Optional)
   ```bash
   pip install Faker
   python3 generate_saas_logs.py
   # Creates: saas_logs.csv and saas_logs.json
   ```

3. **Upload Logs**
   ```
   URL: http://localhost:5000/upload
   
   Steps:
   1. Click or drag-drop file
   2. Select saas_logs.csv or saas_logs.json
   3. Click Upload
   4. Wait 10-20 seconds for processing
   ```

4. **View Dashboard**
   ```
   URL: http://localhost:5000/
   
   See:
   - 9 KPIs with real data
   - Auto-refresh every 30 seconds
   - Sparkline charts
   - System health status
   ```

5. **Search Logs**
   ```
   URL: http://localhost:5000/search
   
   Filters:
   - Text search
   - Log level
   - Date range
   - Endpoint
   - Status code
   - Server
   ```

6. **View in Kibana**
   ```
   URL: http://localhost:5601
   
   Steps:
   1. Stack Management → Index Patterns
   2. Create pattern: saas-logs-*
   3. Time field: @timestamp
   4. View visualizations
   ```

### Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **Web App** | http://localhost:5000 | Register your own |
| **Kibana** | http://localhost:5601 | None (dev mode) |
| **MongoDB** | mongodb://localhost:27017 | admin / password123 |
| **Redis** | redis://localhost:6379 | None |
| **Elasticsearch** | http://localhost:9200 | None |

### Stop Services

```bash
# Stop all services (keep data)
docker-compose stop

# Stop and remove containers (keep data)
docker-compose down

# Stop and remove everything (DELETE DATA!)
docker-compose down -v
```

---

## 📡 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "confirm_password": "SecurePass123"
}

Response: 201 Created
{
  "message": "User registered successfully",
  "user_id": "60d5ec49c1b4a1234567890a"
}
```

#### Login User
```http
POST /api/login
Content-Type: application/json

{
  "username_or_email": "john_doe",
  "password": "SecurePass123"
}

Response: 200 OK
{
  "message": "Login successful",
  "username": "john_doe"
}
```

#### Logout
```http
POST /api/logout

Response: 200 OK
{
  "message": "Logged out successfully"
}
```

### Dashboard Endpoints

#### Get Dashboard Statistics
```http
GET /api/stats

Response: 200 OK
{
  "total_logs": 10000,
  "logs_24h": 2500,
  "error_rate": 12.5,
  "avg_response_time": 245,
  "slowest_endpoints": [
    {
      "endpoint": "/api/reports",
      "avg_time": 1523
    }
  ],
  "active_users": 156,
  "latest_error": {
    "timestamp": "2026-01-01T13:05:29",
    "level": "ERROR",
    "message": "Database connection timeout"
  },
  "uploaded_files": 5,
  "system_health": {
    "elasticsearch": "green",
    "mongodb": "green",
    "redis": "green"
  }
}
```

### Search Endpoints

#### Search Logs
```http
POST /api/search
Content-Type: application/json

{
  "query": "error",
  "level": "ERROR",
  "start_date": "2026-01-01",
  "end_date": "2026-01-02",
  "endpoint": "/api/users",
  "status_code": "500",
  "page": 1,
  "per_page": 50
}

Response: 200 OK
{
  "total": 125,
  "page": 1,
  "per_page": 50,
  "results": [
    {
      "timestamp": "2026-01-01T10:30:45",
      "level": "ERROR",
      "message": "Database connection failed",
      "endpoint": "/api/users",
      "status_code": 500,
      "response_time": 5000
    }
  ]
}
```

#### Export Search Results
```http
POST /api/search/export
Content-Type: application/json

{
  "query": "error",
  "level": "ERROR",
  "start_date": "2026-01-01",
  "end_date": "2026-01-02"
}

Response: 200 OK
(Downloads CSV file)
```

### File Upload Endpoints

#### Upload File
```http
POST /api/upload
Content-Type: multipart/form-data

{
  "file": [binary file data]
}

Response: 201 Created
{
  "message": "File uploaded successfully",
  "file_id": "507f1f77bcf86cd799439011",
  "filename": "1767273715_saas_logs.csv",
  "size": 5242880,
  "record_count": 10000,
  "status": "completed"
}
```

#### List Uploaded Files
```http
GET /api/uploads

Response: 200 OK
{
  "total": 5,
  "files": [
    {
      "file_id": "507f1f77bcf86cd799439011",
      "filename": "1767273715_saas_logs.csv",
      "size": 5242880,
      "record_count": 10000,
      "uploaded_at": "2026-01-01T11:30:00",
      "status": "completed"
    }
  ]
}
```

#### Delete File
```http
DELETE /api/uploads/{file_id}

Response: 200 OK
{
  "message": "File deleted successfully"
}
```

### Health Check

```http
GET /api/health

Response: 200 OK
{
  "status": "healthy",
  "elasticsearch": {
    "status": "green",
    "version": "8.11.0"
  },
  "mongodb": {
    "status": "connected",
    "users_count": 42
  },
  "redis": {
    "status": "connected",
    "memory_usage": "2.5MB"
  },
  "uptime": 3600
}
```

---

## 🗄️ Database Schema

### MongoDB Collections

#### Users Collection
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "username": "john_doe",
  "email": "john@example.com",
  "password_hash": "$2b$12$...",
  "created_at": ISODate("2026-01-01T10:00:00Z"),
  "updated_at": ISODate("2026-01-01T10:00:00Z"),
  "last_login": ISODate("2026-01-01T12:30:00Z"),
  "is_active": true
}
```

#### Files Collection
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439012"),
  "file_id": "507f1f77bcf86cd799439012",
  "user_id": "507f1f77bcf86cd799439011",
  "filename": "saas_logs.csv",
  "original_filename": "saas_logs.csv",
  "file_type": "csv",
  "size_bytes": 5242880,
  "record_count": 10000,
  "status": "completed",
  "uploaded_at": ISODate("2026-01-01T11:30:00Z"),
  "processed_at": ISODate("2026-01-01T11:35:00Z"),
  "error_message": null
}
```

### Elasticsearch Index

#### Index Name Format
```
saas-logs-YYYY.MM.dd
Example: saas-logs-2026.01.01
```

#### Log Document Schema
```json
{
  "@timestamp": "2026-01-01T10:30:45.123Z",
  "timestamp": "2026-01-01 10:30:45",
  "log_type": "web_request",
  "level": "INFO",
  "message": "User login successful",
  "endpoint": "/api/auth/login",
  "http_method": "POST",
  "status_code": 200,
  "response_time_ms": 145,
  "client_ip": "192.168.1.100",
  "geoip": {
    "country_code": "US",
    "country_name": "United States",
    "city": "New York",
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "user_id": "user_1234",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "1861964d-b444-4e50-a89f-c7810cd87e56",
  "request_size": 2048,
  "response_size": 4096,
  "server": "server-01",
  "environment": "production",
  "region": "us-west-2",
  "tenant_id": "tenant_42",
  "instance_id": "i-0a1b2c3d4e5f6g7h8"
}
```

### Redis Keys

```
# Session keys
session:[session_id]
TTL: 604800 seconds (7 days)

# Dashboard cache
cache:dashboard:stats:[user_id]
TTL: 30 seconds

# Rate limiting
rate_limit:[ip_address]
TTL: 3600 seconds
```

---

## 🔧 Development Guide

### Project Setup for Developers

```bash
# 1. Clone repository
git clone <repository-url>
cd saas-monitoring-platform

# 2. Create virtual environment (optional, for local development)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r app/requirements.txt

# 4. Start Docker containers
docker-compose up -d

# 5. Run application
cd app
flask run
```

### File Structure for Development

```
app/
├── app.py              # Main Flask application (1353 lines)
├── requirements.txt    # Python dependencies
├── models/
│   └── user.py        # User model with bcrypt
├── templates/         # Jinja2 HTML templates
└── uploads/           # User file uploads
```

### Key Files & Their Responsibilities

#### `app/app.py` (Main Application)
- **Lines 1-50:** Imports and Flask initialization
- **Lines 51-100:** Configuration and connection setup
- **Lines 101-200:** Helper functions and decorators
- **Lines 201-450:** Authentication routes (register, login, logout)
- **Lines 451-850:** Dashboard routes and statistics
- **Lines 851-1000:** Search functionality
- **Lines 1001-1170:** File upload routes
- **Lines 1171-1353:** API endpoints and utility functions

#### `app/models/user.py`
Handles user authentication:
- User registration with validation
- Password hashing with bcrypt
- Login verification
- Session management

#### `logstash/pipeline/logstash.conf`
ETL pipeline configuration:
- File input from `/uploads/`
- CSV/JSON parsing
- Field extraction and type conversion
- GeoIP enrichment
- Elasticsearch output

#### `generate_saas_logs.py`
Test data generation:
- Creates 10,000 realistic log entries
- Uses Faker for randomization
- Outputs CSV and JSONL formats
- Configurable time ranges

### Adding New Features

#### Add a New API Endpoint
```python
# In app/app.py

@app.route('/api/new-endpoint', methods=['GET', 'POST'])
@login_required
def new_endpoint():
    """
    Endpoint description here
    
    Returns:
        dict: JSON response
    """
    data = request.get_json()
    
    # Your logic here
    
    return jsonify({
        "status": "success",
        "data": result
    }), 200
```

#### Add a New Search Filter
```python
# In app/app.py, search_logs() function

# Add new filter parameter
if request.json.get('new_filter'):
    query_filters.append({
        "term": {"field_name": request.json.get('new_filter')}
    })
```

#### Add a New Dashboard KPI
```python
# In app/app.py, get_dashboard_stats() function

# Calculate new metric
new_metric = es.search(
    index="saas-logs-*",
    body={"aggs": {}}
)

stats['new_metric'] = new_metric['value']
```

### Testing

```bash
# Generate test data
python3 generate_saas_logs.py

# Upload via web UI or manually
cp saas_logs.csv uploads/

# Check Elasticsearch
curl http://localhost:9200/saas-logs-*/_count

# Test API endpoints
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "error"}'
```

### Code Style

- **Python:** Follow PEP 8
- **JavaScript:** Use ES6+ features
- **HTML/CSS:** Use semantic HTML, Bootstrap 5 classes
- **Comments:** Docstrings for functions, inline comments for complex logic

### Debugging

```bash
# View Flask logs
docker-compose logs -f saas-webapp

# View Logstash logs
docker-compose logs -f saas-logstash

# Access Flask console
docker exec -it saas-webapp flask shell

# Check Elasticsearch directly
curl http://localhost:9200/_search?pretty

# MongoDB query
docker exec -it saas-mongodb mongosh -u admin -p password123
use saas_logs
db.users.find()
```

---

## 🐛 Troubleshooting

### Problem: Port Already in Use
```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "5001:5000"
```

### Problem: Elasticsearch Memory Error
```bash
# Increase Docker memory to 4GB in Docker Desktop Settings
# Or reduce ES memory:

docker-compose.yml:
elasticsearch:
  environment:
    - ES_JAVA_OPTS=-Xms256m -Xmx256m
```

### Problem: Services Unhealthy
```bash
# Restart services
docker-compose restart

# Check logs
docker-compose logs

# Complete rebuild
docker-compose down
docker-compose up -d --build
```

### Problem: No Logs in Dashboard
```bash
# Check Elasticsearch has data
curl http://localhost:9200/saas-logs-*/_count

# Check Logstash processing
docker logs saas-logstash --tail 50

# Check uploaded files
ls -la uploads/
ls -la app/uploads/

# Verify file format (must be JSONL, not pretty-printed)
head -1 uploads/filename.json
```

### Problem: Login Not Working
```bash
# Check MongoDB
docker exec -it saas-mongodb mongosh -u admin -p password123
use saas_logs
db.users.find()

# Check Redis sessions
docker exec -it saas-redis redis-cli
KEYS "session:*"
```

### Problem: File Upload Fails
```bash
# Check upload folder permissions
docker exec -it saas-webapp ls -la /uploads

# Check Flask logs
docker logs saas-webapp --tail 20

# Verify file format (CSV or JSON only)
file uploads/filename
```

---

## 📝 Contributing

### How to Contribute

1. **Fork the repository**
   ```bash
   git clone <your-fork-url>
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow code style guidelines
   - Add tests if applicable
   - Update documentation

4. **Commit changes**
   ```bash
   git commit -m "feat: Add your feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Describe your changes clearly
   - Link any related issues
   - Include screenshots for UI changes

### Development Best Practices

- ✅ Write clean, readable code
- ✅ Use meaningful variable names
- ✅ Add docstrings to functions
- ✅ Test before submitting PR
- ✅ Keep commits atomic and focused
- ✅ Update documentation when needed

### Code Review Process

1. All PRs require code review
2. At least one approval required
3. CI/CD checks must pass
4. No conflicts with main branch
5. Squash commits before merge

---

## 📚 Additional Resources

### Documentation
- [`QUICK_START.md`](QUICK_START.md) - Getting started guide
- [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) - Command cheatsheet
- [`docs/IMPLEMENTATION_SUMMARY.md`](docs/IMPLEMENTATION_SUMMARY.md) - Technical details
- [`docs/KIBANA_SETUP.md`](docs/KIBANA_SETUP.md) - Visualization guide

### External Links
- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Logstash Documentation](https://www.elastic.co/guide/en/logstash/current/index.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Docker Documentation](https://docs.docker.com/)

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Authors & Contributors

**Project Lead:** [Your Name]  
**Last Updated:** January 2026

### Acknowledgments
- Built with the ELK Stack (Elasticsearch, Logstash, Kibana)
- Powered by Flask and Python
- Containerized with Docker

---

## 📞 Support & Contact

For issues, questions, or suggestions:

1. **Check existing documentation** in `docs/` folder
2. **Review troubleshooting guide** above
3. **Check application logs:** `docker-compose logs`
4. **Create an issue** on GitHub with detailed information

---

## 🎯 Roadmap

### Version 1.0 (Current) ✅
- ✅ User authentication
- ✅ File upload (CSV/JSON)
- ✅ Log search and filtering
- ✅ Dashboard with 9 KPIs
- ✅ Kibana integration
- ✅ System health monitoring

### Version 1.1 (Planned)
- [ ] Real-time log streaming
- [ ] Alert system
- [ ] Custom dashboard builder
- [ ] Advanced analytics
- [ ] Multi-tenant improvements

### Version 2.0 (Future)
- [ ] Mobile app
- [ ] Machine learning anomaly detection
- [ ] Automated remediation
- [ ] Advanced RBAC
- [ ] Enterprise features

---

## 📊 Project Statistics

- **Total Lines of Code:** 1,500+
- **API Endpoints:** 15+
- **Database Collections:** 2
- **Container Services:** 6
- **Test Log Entries:** 10,000+
- **Setup Time:** 5 minutes
- **Documentation Pages:** 10+

---

**Happy Monitoring! 🚀**

For the latest updates and information, visit the [GitHub Repository](https://github.com/AdemMami123/saas-monitoring-platform).
