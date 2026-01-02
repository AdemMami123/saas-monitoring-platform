#!/usr/bin/env python3
"""
Real-Time Log Test Generator
Sends test logs to various streaming endpoints for testing the real-time module
"""

import json
import time
import random
import socket
import requests
from datetime import datetime
import argparse

# Configuration
LOGSTASH_TCP_HOST = 'localhost'
LOGSTASH_TCP_PORT = 5045
LOGSTASH_HTTP_URL = 'http://localhost:8080'
FLASK_WEBHOOK_URL = 'http://localhost:5000/api/realtime/publish'

# Sample data
LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG_TYPES = ['API', 'DATABASE', 'AUTH', 'SYSTEM']
ENDPOINTS = [
    '/api/users',
    '/api/products',
    '/api/orders',
    '/api/auth/login',
    '/api/auth/logout',
    '/api/payments',
    '/api/settings'
]
METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
STATUS_CODES = [200, 201, 204, 400, 401, 403, 404, 409, 500, 502, 503]
MESSAGES = [
    'Operation completed successfully',
    'Request processed',
    'Database query executed',
    'User authentication successful',
    'Payment processed',
    'Order created',
    'Data validation failed',
    'Connection timeout',
    'Resource not found',
    'Internal server error',
    'High memory usage detected',
    'Disk space low',
    'Service unavailable'
]

def generate_log():
    """Generate a random log entry"""
    level = random.choice(LOG_LEVELS)
    
    # Adjust probability - fewer errors
    if random.random() > 0.8:
        level = random.choice(['ERROR', 'CRITICAL'])
    elif random.random() > 0.5:
        level = random.choice(['WARNING', 'INFO'])
    else:
        level = 'INFO'
    
    log = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'level': level,
        'log_type': random.choice(LOG_TYPES),
        'client_ip': f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
        'user_id': f"user_{random.randint(1000, 9999)}",
        'method': random.choice(METHODS),
        'endpoint': random.choice(ENDPOINTS),
        'status_code': random.choice(STATUS_CODES),
        'response_time_ms': round(random.uniform(10, 3000), 2),
        'message': random.choice(MESSAGES),
        'server': f"server-{random.randint(1, 5)}",
        'tenant_id': f"tenant_{random.randint(1, 10)}"
    }
    
    return log

def send_via_tcp(log):
    """Send log via TCP socket"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((LOGSTASH_TCP_HOST, LOGSTASH_TCP_PORT))
        s.send(json.dumps(log).encode() + b'\n')
        s.close()
        return True
    except Exception as e:
        print(f"TCP Error: {e}")
        return False

def send_via_http_logstash(log):
    """Send log via HTTP to Logstash"""
    try:
        response = requests.post(LOGSTASH_HTTP_URL, json=log, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"HTTP (Logstash) Error: {e}")
        return False

def send_via_flask_webhook(log):
    """Send log via Flask webhook"""
    try:
        response = requests.post(FLASK_WEBHOOK_URL, json=log, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"HTTP (Flask) Error: {e}")
        return False

def continuous_mode(method, rate):
    """Continuously send logs"""
    print(f"\n🚀 Starting continuous log generation")
    print(f"   Method: {method}")
    print(f"   Rate: {rate} logs/second")
    print(f"   Press Ctrl+C to stop\n")
    
    count = 0
    errors = 0
    start_time = time.time()
    
    try:
        while True:
            log = generate_log()
            
            success = False
            if method == 'tcp':
                success = send_via_tcp(log)
            elif method == 'http':
                success = send_via_http_logstash(log)
            elif method == 'webhook':
                success = send_via_flask_webhook(log)
            
            if success:
                count += 1
                print(f"✓ Sent log #{count} - {log['level']} - {log['message'][:50]}")
            else:
                errors += 1
                print(f"✗ Failed to send log (errors: {errors})")
            
            # Sleep to maintain rate
            time.sleep(1.0 / rate)
            
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n\n📊 Summary:")
        print(f"   Total logs sent: {count}")
        print(f"   Errors: {errors}")
        print(f"   Duration: {elapsed:.2f} seconds")
        print(f"   Average rate: {count/elapsed:.2f} logs/sec")

def burst_mode(method, count):
    """Send a burst of logs"""
    print(f"\n💥 Sending burst of {count} logs via {method}")
    
    success_count = 0
    start_time = time.time()
    
    for i in range(count):
        log = generate_log()
        
        success = False
        if method == 'tcp':
            success = send_via_tcp(log)
        elif method == 'http':
            success = send_via_http_logstash(log)
        elif method == 'webhook':
            success = send_via_flask_webhook(log)
        
        if success:
            success_count += 1
            print(f"  [{i+1}/{count}] ✓ {log['level']} - {log['message'][:40]}")
        else:
            print(f"  [{i+1}/{count}] ✗ Failed")
        
        # Small delay to avoid overwhelming
        time.sleep(0.1)
    
    elapsed = time.time() - start_time
    print(f"\n📊 Burst complete:")
    print(f"   Success: {success_count}/{count}")
    print(f"   Duration: {elapsed:.2f} seconds")
    print(f"   Rate: {success_count/elapsed:.2f} logs/sec")

def single_mode(method, level):
    """Send a single log"""
    log = generate_log()
    
    if level:
        log['level'] = level.upper()
    
    print(f"\n📤 Sending single log:")
    print(f"   Level: {log['level']}")
    print(f"   Type: {log['log_type']}")
    print(f"   Message: {log['message']}")
    print(f"   Method: {method}")
    
    success = False
    if method == 'tcp':
        success = send_via_tcp(log)
    elif method == 'http':
        success = send_via_http_logstash(log)
    elif method == 'webhook':
        success = send_via_flask_webhook(log)
    
    if success:
        print(f"\n✅ Log sent successfully!")
    else:
        print(f"\n❌ Failed to send log")
    
    print(f"\n📄 Full log data:")
    print(json.dumps(log, indent=2))

def main():
    parser = argparse.ArgumentParser(
        description='Send test logs to real-time monitoring system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Send a single log via HTTP
  python send_test_logs.py single --method http
  
  # Send a single ERROR log
  python send_test_logs.py single --level error
  
  # Send 50 logs as fast as possible
  python send_test_logs.py burst --count 50
  
  # Continuously send logs at 5/second
  python send_test_logs.py continuous --rate 5
  
  # Send logs via TCP socket
  python send_test_logs.py continuous --method tcp --rate 10
        '''
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='Operation mode')
    
    # Single log mode
    single_parser = subparsers.add_parser('single', help='Send a single log')
    single_parser.add_argument('--method', choices=['tcp', 'http', 'webhook'], 
                               default='http', help='Sending method')
    single_parser.add_argument('--level', choices=['debug', 'info', 'warning', 'error', 'critical'],
                               help='Log level (optional)')
    
    # Burst mode
    burst_parser = subparsers.add_parser('burst', help='Send a burst of logs')
    burst_parser.add_argument('--method', choices=['tcp', 'http', 'webhook'],
                              default='http', help='Sending method')
    burst_parser.add_argument('--count', type=int, default=10,
                              help='Number of logs to send')
    
    # Continuous mode
    continuous_parser = subparsers.add_parser('continuous', help='Continuously send logs')
    continuous_parser.add_argument('--method', choices=['tcp', 'http', 'webhook'],
                                   default='http', help='Sending method')
    continuous_parser.add_argument('--rate', type=float, default=1.0,
                                   help='Logs per second')
    
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        return
    
    print("=" * 60)
    print("  Real-Time Log Test Generator")
    print("=" * 60)
    
    if args.mode == 'single':
        single_mode(args.method, args.level if hasattr(args, 'level') else None)
    elif args.mode == 'burst':
        burst_mode(args.method, args.count)
    elif args.mode == 'continuous':
        continuous_mode(args.method, args.rate)

if __name__ == '__main__':
    main()
