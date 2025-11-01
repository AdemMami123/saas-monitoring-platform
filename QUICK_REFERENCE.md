# 🚀 Quick Reference Card

## Start Services
```bash
docker-compose up -d
```

## Generate Sample Logs
```bash
# Install dependency (first time only)
pip install Faker

# Generate 10,000 logs
python3 generate_logs.py
```

## Access Interfaces
- **Dashboard** (Enhanced!): http://localhost:5000
  - 9 Real-time KPIs with auto-refresh
  - Error rate, response time, active users
  - Slowest endpoints, latest error alerts
  - System health monitoring
- **Upload**: http://localhost:5000/upload
- **Search**: http://localhost:5000/search
- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200

## Upload Logs
**Web UI**: Drag & drop at http://localhost:5000/upload

**API**:
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@uploads/generated_logs.csv"
```

## Check Status
```bash
# Services
docker-compose ps

# Elasticsearch
curl http://localhost:9200/_cluster/health

# Log count
curl http://localhost:9200/saas-logs-*/_count

# Logstash logs
docker logs saas-logstash --tail 50
```

## Kibana Setup
1. Open http://localhost:5601
2. Stack Management → Index Patterns
3. Create pattern: `saas-logs-*`
4. Time field: `@timestamp`
5. Follow: `docs/KIBANA_SETUP.md`

## API Endpoints
```bash
# Health check
GET /api/health

# Stats & KPIs (Enhanced!)
GET /api/stats

# Upload file
POST /api/upload

# List uploads
GET /api/uploads

# Delete upload
DELETE /api/uploads/<file_id>

# Search logs
POST /api/search

# Get endpoints list
GET /api/search/endpoints

# Export logs
POST /api/logs/export
```

## Troubleshooting
```bash
# Restart Logstash
docker restart saas-logstash

# View logs
docker logs saas-app
docker logs saas-logstash
docker logs saas-elasticsearch

# Clean restart
docker-compose down
docker-compose up -d
```

## Documentation
- **Dashboard Enhancement**: `docs/DASHBOARD_ENHANCEMENT.md` ⭐ NEW!
- **Search Functionality**: `docs/SEARCH_FUNCTIONALITY.md`
- **Upload Functionality**: `docs/UPLOAD_FUNCTIONALITY.md`
- **Kibana Setup**: `docs/KIBANA_SETUP.md`
- **Log Generation**: `docs/GENERATE_LOGS_GUIDE.md`
- **Full Summary**: `docs/IMPLEMENTATION_SUMMARY.md`
