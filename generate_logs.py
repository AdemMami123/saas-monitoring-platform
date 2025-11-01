#!/usr/bin/env python3
"""
Generate realistic SaaS application logs for testing and demonstration purposes.
Creates 10,000 log entries with realistic data using Faker library.
Outputs both CSV and JSON formats.
"""

import csv
import json
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker
fake = Faker()

# Configuration
NUM_LOGS = 10000
OUTPUT_CSV = 'uploads/generated_logs.csv'
OUTPUT_JSON = 'uploads/generated_logs.json'

# Define realistic SaaS API endpoints
ENDPOINTS = [
    '/api/users',
    '/api/users/{id}',
    '/api/auth/login',
    '/api/auth/logout',
    '/api/auth/refresh',
    '/api/products',
    '/api/products/{id}',
    '/api/orders',
    '/api/orders/{id}',
    '/api/payments',
    '/api/payments/process',
    '/api/search',
    '/api/analytics',
    '/api/dashboard',
    '/api/settings',
    '/api/profile',
    '/api/notifications',
    '/api/webhooks',
    '/api/integrations',
    '/api/reports',
    '/api/export',
    '/api/import',
    '/api/billing',
    '/api/subscriptions',
    '/api/teams',
    '/api/projects',
    '/api/tasks',
    '/api/comments',
    '/api/files/upload',
    '/api/files/download',
]

# Log levels with realistic distribution
LOG_LEVELS = [
    ('INFO', 0.70),      # 70% INFO
    ('WARNING', 0.15),   # 15% WARNING
    ('ERROR', 0.10),     # 10% ERROR
    ('DEBUG', 0.04),     # 4% DEBUG
    ('CRITICAL', 0.01),  # 1% CRITICAL
]

# HTTP status codes with realistic distribution
STATUS_CODES = [
    (200, 0.65),   # 65% Success
    (201, 0.10),   # 10% Created
    (400, 0.08),   # 8% Bad Request
    (401, 0.05),   # 5% Unauthorized
    (403, 0.03),   # 3% Forbidden
    (404, 0.05),   # 5% Not Found
    (500, 0.03),   # 3% Internal Server Error
    (503, 0.01),   # 1% Service Unavailable
]

# HTTP methods
HTTP_METHODS = [
    ('GET', 0.50),
    ('POST', 0.25),
    ('PUT', 0.12),
    ('DELETE', 0.08),
    ('PATCH', 0.05),
]

def weighted_choice(choices):
    """Select an item based on weighted probabilities"""
    total = sum(weight for choice, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for choice, weight in choices:
        if upto + weight >= r:
            return choice
        upto += weight
    return choices[0][0]

def generate_response_time(status_code, log_level):
    """Generate realistic response time based on status code and log level"""
    if status_code >= 500 or log_level == 'CRITICAL':
        # Server errors are slower
        return random.randint(2000, 10000)
    elif status_code >= 400:
        # Client errors
        return random.randint(100, 1000)
    elif log_level == 'WARNING':
        return random.randint(500, 2000)
    else:
        # Normal responses
        return random.randint(50, 800)

def generate_error_message(status_code, endpoint):
    """Generate appropriate error message based on status code"""
    error_messages = {
        400: [
            "Invalid request parameters",
            "Missing required field: email",
            "Invalid JSON format",
            "Validation failed",
        ],
        401: [
            "Authentication token expired",
            "Invalid credentials",
            "Unauthorized access",
            "Token not found",
        ],
        403: [
            "Insufficient permissions",
            "Access denied",
            "Resource forbidden",
            "Permission denied for this resource",
        ],
        404: [
            "Resource not found",
            "Endpoint does not exist",
            "User not found",
            "Record not found in database",
        ],
        500: [
            "Internal server error",
            "Database connection failed",
            "Unhandled exception occurred",
            "Service temporarily unavailable",
        ],
        503: [
            "Service unavailable",
            "Database timeout",
            "Too many concurrent requests",
            "Downstream service unreachable",
        ],
    }
    
    if status_code in error_messages:
        return random.choice(error_messages[status_code])
    else:
        return f"Request processed successfully"

def generate_log_entry(timestamp):
    """Generate a single realistic log entry"""
    # Select weighted random values
    log_level = weighted_choice(LOG_LEVELS)
    status_code = weighted_choice(STATUS_CODES)
    http_method = weighted_choice(HTTP_METHODS)
    endpoint = random.choice(ENDPOINTS)
    
    # Replace {id} with actual ID
    if '{id}' in endpoint:
        endpoint = endpoint.replace('{id}', str(random.randint(1, 10000)))
    
    # Generate response time
    response_time = generate_response_time(status_code, log_level)
    
    # Generate user data
    user_id = f"user_{random.randint(1, 5000)}"
    ip_address = fake.ipv4()
    user_agent = fake.user_agent()
    
    # Generate message
    if status_code >= 400:
        message = generate_error_message(status_code, endpoint)
    else:
        message = f"{http_method} {endpoint} completed successfully"
    
    # Additional fields
    request_id = fake.uuid4()
    session_id = fake.uuid4()
    
    # Calculate size
    request_size = random.randint(100, 5000)
    response_size = random.randint(500, 50000)
    
    log_entry = {
        '@timestamp': timestamp.isoformat(),
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'level': log_level,
        'message': message,
        'endpoint': endpoint,
        'http_method': http_method,
        'status_code': status_code,
        'response_time': response_time,
        'user_id': user_id,
        'ip_address': ip_address,
        'user_agent': user_agent,
        'request_id': request_id,
        'session_id': session_id,
        'request_size': request_size,
        'response_size': response_size,
        'environment': random.choice(['production', 'staging', 'development']),
        'region': random.choice(['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']),
        'instance_id': f"i-{fake.hexify(text='^^^^^^^^^^^^^^^^', upper=False)}",
    }
    
    return log_entry

def generate_logs():
    """Generate all log entries"""
    print(f"Generating {NUM_LOGS} log entries...")
    
    logs = []
    
    # Generate logs over the past 7 days
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)
    
    for i in range(NUM_LOGS):
        # Random timestamp within the range
        time_delta = random.random() * (end_time - start_time).total_seconds()
        timestamp = start_time + timedelta(seconds=time_delta)
        
        log_entry = generate_log_entry(timestamp)
        logs.append(log_entry)
        
        if (i + 1) % 1000 == 0:
            print(f"  Generated {i + 1} logs...")
    
    # Sort logs by timestamp
    logs.sort(key=lambda x: x['@timestamp'])
    
    print(f"✓ Generated {NUM_LOGS} logs successfully")
    return logs

def save_as_csv(logs, filename):
    """Save logs as CSV file"""
    print(f"\nSaving logs to {filename}...")
    
    # Define CSV columns
    fieldnames = [
        '@timestamp',
        'timestamp',
        'level',
        'message',
        'endpoint',
        'http_method',
        'status_code',
        'response_time',
        'user_id',
        'ip_address',
        'user_agent',
        'request_id',
        'session_id',
        'request_size',
        'response_size',
        'environment',
        'region',
        'instance_id',
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(logs)
    
    print(f"✓ CSV file saved successfully")

def save_as_json(logs, filename):
    """Save logs as JSON file"""
    print(f"\nSaving logs to {filename}...")
    
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(logs, jsonfile, indent=2)
    
    print(f"✓ JSON file saved successfully")

def print_statistics(logs):
    """Print statistics about generated logs"""
    print("\n" + "="*60)
    print("LOG GENERATION STATISTICS")
    print("="*60)
    
    # Count by log level
    level_counts = {}
    for log in logs:
        level = log['level']
        level_counts[level] = level_counts.get(level, 0) + 1
    
    print("\nLog Levels:")
    for level, count in sorted(level_counts.items()):
        percentage = (count / len(logs)) * 100
        print(f"  {level:10s}: {count:5d} ({percentage:5.2f}%)")
    
    # Count by status code
    status_counts = {}
    for log in logs:
        status = log['status_code']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\nStatus Codes:")
    for status, count in sorted(status_counts.items()):
        percentage = (count / len(logs)) * 100
        print(f"  {status:3d}: {count:5d} ({percentage:5.2f}%)")
    
    # Response time statistics
    response_times = [log['response_time'] for log in logs]
    avg_response_time = sum(response_times) / len(response_times)
    max_response_time = max(response_times)
    min_response_time = min(response_times)
    
    print("\nResponse Times:")
    print(f"  Average: {avg_response_time:.2f}ms")
    print(f"  Min:     {min_response_time}ms")
    print(f"  Max:     {max_response_time}ms")
    
    # Time range
    print("\nTime Range:")
    print(f"  Start: {logs[0]['timestamp']}")
    print(f"  End:   {logs[-1]['timestamp']}")
    
    print("\n" + "="*60)

def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("SaaS LOG GENERATOR")
    print("="*60 + "\n")
    
    # Generate logs
    logs = generate_logs()
    
    # Save in both formats
    save_as_csv(logs, OUTPUT_CSV)
    save_as_json(logs, OUTPUT_JSON)
    
    # Print statistics
    print_statistics(logs)
    
    print("\n✓ Log generation complete!")
    print(f"\nOutput files:")
    print(f"  - {OUTPUT_CSV}")
    print(f"  - {OUTPUT_JSON}")
    print("\nYou can now upload these files using the web interface at /upload")
    print()

if __name__ == '__main__':
    main()
