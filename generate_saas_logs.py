import csv
import json
import random
from datetime import datetime, timedelta
from faker import Faker
from collections import Counter

fake = Faker()

# Configuration
NUM_LOGS = 10000
DAYS_BACK = 30

# Distributions
LOG_TYPES = ['web_request', 'database_query']
LEVELS = {
    'INFO': 0.70,
    'WARNING': 0.15,
    'ERROR': 0.10,
    'CRITICAL': 0.05
}
METHODS = {
    'GET': 0.60,
    'POST': 0.25,
    'PUT': 0.10,
    'DELETE': 0.05
}
ENDPOINTS = [
    '/api/auth/login',
    '/api/users',
    '/api/orders',
    '/api/products',
    '/api/analytics/dashboard',
    '/api/settings',
    '/api/integrations',
    '/api/webhooks',
    '/api/reports',
    '/api/billing'
]
STATUS_CODES = {
    200: 0.70,
    201: 0.05,
    400: 0.10,
    404: 0.05,
    500: 0.03,
    503: 0.02,
    401: 0.05
}
SERVERS = ['server-01', 'server-02', 'server-03', 'server-04', 'server-05']

# SQL Query templates
SQL_QUERIES = [
    "SELECT * FROM users WHERE user_id = {user_id}",
    "SELECT * FROM orders WHERE tenant_id = '{tenant_id}' ORDER BY created_at DESC LIMIT 10",
    "UPDATE users SET last_login = NOW() WHERE user_id = {user_id}",
    "INSERT INTO audit_logs (user_id, action, timestamp) VALUES ({user_id}, 'login', NOW())",
    "SELECT COUNT(*) FROM products WHERE tenant_id = '{tenant_id}'",
    "DELETE FROM sessions WHERE user_id = {user_id} AND expired = true",
    "SELECT * FROM analytics WHERE tenant_id = '{tenant_id}' AND date >= NOW() - INTERVAL '7 days'",
    "UPDATE settings SET value = 'enabled' WHERE tenant_id = '{tenant_id}' AND key = 'notifications'"
]

def weighted_choice(choices):
    """Select item based on weighted probabilities"""
    items = list(choices.keys())
    weights = list(choices.values())
    return random.choices(items, weights=weights, k=1)[0]

def generate_response_time():
    """Generate response time with realistic distribution"""
    rand = random.random()
    if rand < 0.85:  # 85% normal range
        return random.randint(10, 500)
    elif rand < 0.97:  # 12% slow
        return random.randint(500, 3000)
    else:  # 3% very slow
        return random.randint(3000, 5000)

def generate_message(status_code, endpoint, method):
    """Generate descriptive log message based on status"""
    messages = {
        200: f"Successfully processed {method} request to {endpoint}",
        201: f"Resource created successfully at {endpoint}",
        400: f"Bad request to {endpoint} - Invalid parameters",
        404: f"Resource not found at {endpoint}",
        500: f"Internal server error processing {method} {endpoint}",
        503: f"Service temporarily unavailable for {endpoint}",
        401: f"Unauthorized access attempt to {endpoint}"
    }
    return messages.get(status_code, f"Request to {endpoint} completed with status {status_code}")

def generate_log_entry():
    """Generate a single log entry"""
    # Timestamp within last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=DAYS_BACK)
    timestamp = fake.date_time_between(start_date=start_date, end_date=end_date)
    
    # Basic fields
    log_type = random.choice(LOG_TYPES)
    level = weighted_choice(LEVELS)
    client_ip = fake.ipv4()
    
    # User ID (10% null for anonymous)
    user_id = None if random.random() < 0.10 else random.randint(1, 500)
    
    # HTTP fields
    method = weighted_choice(METHODS)
    endpoint = random.choice(ENDPOINTS)
    status_code = weighted_choice(STATUS_CODES)
    response_time_ms = generate_response_time()
    user_agent = fake.user_agent()
    
    # Message
    message = generate_message(status_code, endpoint, method)
    
    # SQL query (10% of logs)
    sql_query = None
    query_duration_ms = None
    if random.random() < 0.10:
        template = random.choice(SQL_QUERIES)
        tenant_id = f"tenant_{random.randint(1, 50)}"
        sql_query = template.format(user_id=user_id or 0, tenant_id=tenant_id)
        query_duration_ms = random.randint(5, 2000)
    
    # Server and tenant
    server = random.choice(SERVERS)
    tenant_id = f"tenant_{random.randint(1, 50)}"
    
    return {
        'timestamp': timestamp.isoformat(),
        'log_type': log_type,
        'level': level,
        'client_ip': client_ip,
        'user_id': user_id,
        'method': method,
        'endpoint': endpoint,
        'status_code': status_code,
        'response_time_ms': response_time_ms,
        'user_agent': user_agent,
        'message': message,
        'sql_query': sql_query,
        'query_duration_ms': query_duration_ms,
        'server': server,
        'tenant_id': tenant_id
    }

def main():
    print(f"Generating {NUM_LOGS:,} SaaS log entries...")
    
    # Generate logs
    logs = []
    timestamps = []
    status_codes_list = []
    
    for _ in range(NUM_LOGS):
        log = generate_log_entry()
        logs.append(log)
        timestamps.append(log['timestamp'])
        status_codes_list.append(log['status_code'])
    
    # Sort by timestamp
    logs.sort(key=lambda x: x['timestamp'])
    
    print(f"✓ Generated {len(logs):,} logs")
    
    # Date range
    min_date = min(timestamps)
    max_date = max(timestamps)
    print(f"Date range: {min_date[:10]} to {max_date[:10]}\n")
    
    # Status code distribution
    status_counter = Counter(status_codes_list)
    print("Status Code Distribution:")
    for code in sorted(status_counter.keys()):
        count = status_counter[code]
        percentage = (count / NUM_LOGS) * 100
        print(f"  {code}: {count:,} ({percentage:.1f}%)")
    print()
    
    # Save as CSV
    csv_filename = 'saas_logs.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'timestamp', 'log_type', 'level', 'client_ip', 'user_id',
            'method', 'endpoint', 'status_code', 'response_time_ms',
            'user_agent', 'message', 'sql_query', 'query_duration_ms',
            'server', 'tenant_id'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(logs)
    
    # Get CSV file size
    import os
    csv_size = os.path.getsize(csv_filename) / (1024 * 1024)  # MB
    print(f"✓ Saved: {csv_filename} ({csv_size:.1f} MB)")
    
    # Save as JSON
    json_filename = 'saas_logs.json'
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(logs, jsonfile, indent=2)
    
    # Get JSON file size
    json_size = os.path.getsize(json_filename) / (1024 * 1024)  # MB
    print(f"✓ Saved: {json_filename} ({json_size:.1f} MB)")

if __name__ == '__main__':
    main()
