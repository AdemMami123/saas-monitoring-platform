# Generate Logs Script - Quick Start Guide

## Overview

The `generate_logs.py` script generates 10,000 realistic SaaS application logs using the Faker library. It creates both CSV and JSON formats ready for upload and processing.

## Prerequisites

Install the required dependency:

```bash
# Using pip
pip install Faker

# Or using pip3
pip3 install Faker

# Or in a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install Faker
```

## Usage

### Basic Usage

Simply run the script from the project root:

```bash
python3 generate_logs.py
```

Or on Windows:

```bash
python generate_logs.py
```

### Using WSL (Windows Subsystem for Linux)

```bash
wsl -d Ubuntu -e bash -c "cd /home/ademm/saas-monitoring-platform && python3 generate_logs.py"
```

### Using Docker (if Python not installed locally)

```bash
docker run -it --rm -v ${PWD}:/workspace python:3.11 bash -c "cd /workspace && pip install Faker && python generate_logs.py"
```

## Output

The script generates two files in the `uploads/` directory:

1. **generated_logs.csv** - CSV format with headers
2. **generated_logs.json** - JSON array format

### Sample Output

```
============================================================
SaaS LOG GENERATOR
============================================================

Generating 10,000 log entries...
  Generated 1000 logs...
  Generated 2000 logs...
  Generated 3000 logs...
  Generated 4000 logs...
  Generated 5000 logs...
  Generated 6000 logs...
  Generated 7000 logs...
  Generated 8000 logs...
  Generated 9000 logs...
  Generated 10000 logs...
✓ Generated 10,000 logs successfully

Saving logs to uploads/generated_logs.csv...
✓ CSV file saved successfully

Saving logs to uploads/generated_logs.json...
✓ JSON file saved successfully

============================================================
LOG GENERATION STATISTICS
============================================================

Log Levels:
  CRITICAL :    95 ( 0.95%)
  DEBUG    :   399 ( 3.99%)
  ERROR    :   993 ( 9.93%)
  INFO     :  7015 (70.15%)
  WARNING  :  1498 (14.98%)

Status Codes:
  200:  6513 (65.13%)
  201:   998 (9.98%)
  400:   802 (8.02%)
  401:   491 (4.91%)
  403:   304 (3.04%)
  404:   498 (4.98%)
  500:   295 (2.95%)
  503:    99 (0.99%)

Response Times:
  Average: 623.45ms
  Min:     50ms
  Max:     9998ms

Time Range:
  Start: 2025-10-25 12:34:56
  End:   2025-11-01 15:23:45

============================================================

✓ Log generation complete!

Output files:
  - uploads/generated_logs.csv
  - uploads/generated_logs.json

You can now upload these files using the web interface at /upload
```

## Generated Log Fields

Each log entry contains the following fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| @timestamp | ISO8601 | Timestamp in ISO format | 2025-10-25T12:34:56.123456 |
| timestamp | String | Human-readable timestamp | 2025-10-25 12:34:56 |
| level | String | Log severity level | INFO, WARNING, ERROR, DEBUG, CRITICAL |
| message | String | Log message | "GET /api/users completed successfully" |
| endpoint | String | API endpoint | /api/users/123 |
| http_method | String | HTTP method | GET, POST, PUT, DELETE, PATCH |
| status_code | Integer | HTTP status code | 200, 404, 500 |
| response_time | Integer | Response time in milliseconds | 234 |
| user_id | String | User identifier | user_1234 |
| ip_address | String | Client IP address | 192.168.1.100 |
| user_agent | String | Browser/client user agent | Mozilla/5.0... |
| request_id | UUID | Unique request identifier | 550e8400-e29b-41d4-a716-446655440000 |
| session_id | UUID | User session identifier | 550e8400-e29b-41d4-a716-446655440001 |
| request_size | Integer | Request size in bytes | 1024 |
| response_size | Integer | Response size in bytes | 8192 |
| environment | String | Environment name | production, staging, development |
| region | String | AWS region | us-east-1, eu-west-1 |
| instance_id | String | Server instance ID | i-1234567890abcdef0 |

## Configuration

You can modify the script to adjust:

- **Number of logs**: Change `NUM_LOGS = 10000` (line 14)
- **Output location**: Change `OUTPUT_CSV` and `OUTPUT_JSON` paths (lines 15-16)
- **Time range**: Modify the date range in `generate_logs()` function (currently 7 days)
- **API endpoints**: Edit the `ENDPOINTS` list (lines 19-50)
- **Log level distribution**: Adjust `LOG_LEVELS` percentages (lines 53-59)
- **Status code distribution**: Adjust `STATUS_CODES` percentages (lines 62-71)

## Example: Generate More Logs

Edit the script to generate 50,000 logs:

```python
# Line 14
NUM_LOGS = 50000  # Changed from 10000
```

## Uploading Generated Logs

### Option 1: Web Interface (Recommended)

1. Start the application: `docker-compose up -d`
2. Navigate to: http://localhost:5000/upload
3. Drag and drop `generated_logs.csv` or `generated_logs.json`
4. Click "Upload File"
5. Logstash will automatically process the file

### Option 2: API Upload

```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@uploads/generated_logs.csv"
```

### Option 3: Direct to Logstash

Files placed in the `uploads/` folder are automatically detected by Logstash and processed into Elasticsearch.

## Viewing Data in Kibana

After uploading:

1. Wait 30-60 seconds for Logstash to process
2. Open Kibana: http://localhost:5601
3. Create index pattern: `saas-logs-*`
4. View data in "Discover" tab
5. Create visualizations using the data

See `docs/KIBANA_SETUP.md` for detailed visualization setup.

## Troubleshooting

### ImportError: No module named 'faker'

**Solution**: Install Faker library
```bash
pip install Faker
```

### Permission Denied Error

**Solution**: Ensure the uploads/ directory exists and is writable
```bash
mkdir -p uploads
chmod 755 uploads
```

### FileNotFoundError: uploads/

**Solution**: Create the uploads directory
```bash
mkdir uploads
```

Or modify the script to use current directory:
```python
OUTPUT_CSV = 'generated_logs.csv'
OUTPUT_JSON = 'generated_logs.json'
```

### Script Runs But No Output

**Solution**: Check if files were created
```bash
ls -lh uploads/
```

If files exist but are empty, there may be an error. Run with verbose output:
```bash
python3 generate_logs.py 2>&1 | tee generate_logs.log
```

## Advanced Usage

### Generate Logs for Specific Time Period

Modify the `generate_logs()` function:

```python
# Generate logs for last 30 days instead of 7
end_time = datetime.utcnow()
start_time = end_time - timedelta(days=30)  # Changed from 7
```

### Filter by Environment

Generate only production logs:

```python
# In generate_log_entry function, replace:
'environment': random.choice(['production', 'staging', 'development'])

# With:
'environment': 'production'
```

### Increase Error Rate

Simulate a system with more errors:

```python
LOG_LEVELS = [
    ('INFO', 0.50),      # Reduced from 70%
    ('WARNING', 0.20),   # Increased
    ('ERROR', 0.20),     # Increased from 10%
    ('DEBUG', 0.05),
    ('CRITICAL', 0.05),  # Increased from 1%
]
```

## Performance

- **10,000 logs**: ~5-10 seconds
- **50,000 logs**: ~25-45 seconds  
- **100,000 logs**: ~50-90 seconds

File sizes (approximate):
- **CSV**: 1.5-2 MB per 10,000 logs
- **JSON**: 2-2.5 MB per 10,000 logs

## Integration with CI/CD

You can integrate this script into your testing pipeline:

```yaml
# .github/workflows/test.yml
- name: Generate Test Logs
  run: |
    pip install Faker
    python generate_logs.py
    
- name: Upload to Test Environment
  run: |
    curl -X POST http://test-env:5000/api/upload \
      -F "file=@uploads/generated_logs.csv"
```

## License

This script is part of the SaaS Monitoring Platform project.

---

**Questions or Issues?**

Check the main project README or create an issue in the repository.
