# Real-Time Monitoring and Analysis Module

## Overview

This module adds comprehensive real-time monitoring, streaming analytics, and live visualization capabilities to the SaaS Log Monitoring Platform. It enables sub-second latency for log ingestion, processing, and visualization through WebSocket connections and streaming pipelines.

## Features Implemented

### 1. Real-Time Dashboard with WebSocket

**Location:** `/live-dashboard`

**Key Features:**
- WebSocket-based bidirectional communication between browser and server
- Automatic push of new logs to all connected clients
- Real-time charts and graphs with streaming plugin
- Connection status indicator with visual feedback
- Automatic reconnection on connection loss with exponential backoff
- Live metrics counters for instant visibility

**Technology Stack:**
- **Server:** Flask-SocketIO with eventlet async mode
- **Client:** Socket.IO JavaScript client
- **Charts:** Chart.js with chartjs-plugin-streaming

**Metrics Displayed:**
- **Logs Per Second:** Real-time throughput counter
- **Errors Per Minute:** Critical error rate tracking
- **Connected Users:** Active WebSocket connections
- **Total Processed:** Cumulative log count

**Charts:**
- **Log Stream Rate:** Real-time line chart (60-second window)
- **Log Levels:** Doughnut chart showing distribution
- **Response Time Distribution:** Bar chart with latency buckets
- **Status Codes:** Horizontal bar chart of HTTP status codes

### 2. Stream Processing Pipeline

**Location:** Logstash pipeline configuration

**Input Sources:**

| Source Type | Port | Protocol | Use Case |
|------------|------|----------|----------|
| TCP Socket | 5045 (external) → 5000 (internal) | TCP | High-throughput streaming |
| UDP Socket | 5001 | UDP | Low-latency, fire-and-forget logs |
| HTTP Webhook | 8080 | HTTP/HTTPS | Third-party integrations |
| Beats (Filebeat) | 5044 | Beats protocol | Tail log files in real-time |
| Redis Pub/Sub | 6379 | Redis | Message queue integration |
| File (legacy) | - | File system | Batch upload processing |

**Processing Pipeline:**
1. **Input Stage:** Multi-source ingestion
2. **Filter Stage:** Parsing, enrichment, GeoIP lookup
3. **Output Stage:** 
   - Elasticsearch indexing
   - Redis Pub/Sub broadcast (for Flask consumers)

**Performance:**
- **Target Latency:** <1 second end-to-end
- **Throughput:** Supports thousands of logs/second
- **Buffer Management:** Circular buffer with 1000-log limit

### 3. Live Metrics Dashboard

**Real-Time Counters:**

All metrics update every second via WebSocket:

```javascript
{
  "logs_per_second": 42,
  "errors_per_minute": 3,
  "connected_users": 5,
  "total_logs_processed": 125847
}
```

**Chart Updates:**
- **Streaming Line Chart:** Adds data points every second
- **Doughnut Chart:** Updates on new log level detected
- **Bar Charts:** Refresh on data change with smooth animations

**Animation Library:**
- Uses Chart.js streaming plugin
- Luxon for date/time handling
- Smooth transitions with 'none' animation mode for performance

### 4. Live Log Tail Feature

**Location:** `/live-logs`

**Terminal-Style Interface:**
- Dark theme optimized for long-term viewing
- Monospace font (Consolas/Courier New)
- Syntax highlighting by log level
- Professional color scheme

**Color Coding:**

| Log Level | Background | Text | Border |
|-----------|-----------|------|--------|
| INFO | Blue (#0e639c) | White | Blue |
| DEBUG | Gray (#4d4d4d) | Light Gray | Gray |
| WARNING | Yellow-Brown (#755c1b) | White | Yellow |
| ERROR | Red (#a71d2a) | White | Red |
| CRITICAL | Dark Red (#8b0000) | White | Red (pulsing) |

**Controls:**

| Button | Shortcut | Function |
|--------|----------|----------|
| Pause/Resume | Space | Stop/start log stream |
| Clear | Ctrl+C | Clear all displayed logs |
| Auto-scroll | Ctrl+S | Toggle automatic scrolling |
| Level Filter | - | Filter by log level |
| Service Filter | - | Filter by service type |
| Search | Ctrl+F | Text search with highlighting |

**Features:**
- **Circular Buffer:** Max 1000 logs in memory to prevent memory leaks
- **Auto-Scroll:** Automatically scrolls to newest logs
- **Manual Scroll Detection:** Disables auto-scroll when user scrolls up
- **Real-Time Filtering:** Apply filters without page reload
- **Search Highlighting:** Yellow highlight for search terms
- **Statistics Bar:** Shows log count, error count, rate, and buffer size

**Keyboard Shortcuts:**
```
Space      - Pause/Resume log stream
Ctrl+C     - Clear all logs
Ctrl+S     - Toggle auto-scroll
Ctrl+F     - Focus search box
```

### 5. Visual Alerts System

**Desktop Notifications:**

Triggered on ERROR and CRITICAL logs:

```javascript
new Notification('ERROR Alert', {
    body: 'New error detected',
    icon: '/static/alert-icon.png',
    badge: '/static/badge-icon.png',
    tag: 'ERROR'
});
```

**Permission Request:**
- Auto-requested 2 seconds after page load
- Manual button available in dashboard
- Browser-native permission dialog

**Tab Badge:**
- Red circular badge on top-right of page
- Shows count of unread alerts
- Animates with bounce effect
- Resets on window focus

**Alert Sounds:**
- Optional sound notification (base64 embedded WAV)
- Toggle button to enable/disable
- Volume-up/volume-mute icon indicator
- Respects browser autoplay policies

**Visual Flash:**
- Navbar flashes red on critical alerts
- 3 flash cycles, 0.5 seconds each
- Smooth CSS animation
- Non-intrusive, attention-grabbing

**Tab Title Update:**
```
Normal:  "Live Dashboard - Real-Time Monitoring"
Alert:   "(5) ERROR Alert - Live Dashboard"
```

## Architecture

### WebSocket Flow

```
┌─────────────┐         WebSocket          ┌─────────────┐
│   Browser   │ ◄──────────────────────► │  Flask App  │
│  (Client)   │                            │ (SocketIO)  │
└─────────────┘                            └─────────────┘
       ▲                                          │
       │                                          ▼
       │                                   ┌─────────────┐
       │                                   │    Redis    │
       │                                   │  Pub/Sub    │
       │                                   └─────────────┘
       │                                          ▲
       │                                          │
       └──────────── Real-time Logs ─────────────┘
```

### Data Flow

```
Log Sources
    ↓
Logstash (Multi-input)
    ↓
[Filter & Enrich]
    ↓
├─→ Elasticsearch (Storage & Query)
└─→ Redis Pub/Sub (Real-time Broadcast)
    ↓
Flask SocketIO (Listening)
    ↓
WebSocket Emit
    ↓
Browser Clients (Live Update)
```

### Background Threads

The Flask app runs multiple background threads:

1. **Log Simulation Thread** (for testing)
   - Generates random logs every 0.1-2 seconds
   - Disabled in production

2. **Elasticsearch Polling Thread** (optional)
   - Polls for new logs every second
   - Query by timestamp range

3. **Redis Pub/Sub Listener** (recommended for production)
   - Subscribes to 'logs' channel
   - Pushes logs to WebSocket clients

## API Endpoints

### WebSocket Events

**Client → Server:**

```javascript
// Connect and subscribe
socket.emit('subscribe', { channel: 'all' });

// Set filters
socket.emit('set_filters', {
    log_levels: ['ERROR', 'CRITICAL'],
    services: ['API', 'DATABASE'],
    min_response_time: 1000,
    status_codes: [500, 503]
});

// Unsubscribe
socket.emit('unsubscribe', { channel: 'all' });

// Request current metrics
socket.emit('request_metrics');
```

**Server → Client:**

```javascript
// Connection status
socket.on('connection_status', (data) => {
    console.log(data.status, data.client_id);
});

// New log entry
socket.on('new_log', (log) => {
    // Process log entry
});

// Metrics update
socket.on('metrics_update', (metrics) => {
    // Update dashboard counters
});

// Subscription confirmation
socket.on('subscription_confirmed', (data) => {
    console.log('Subscribed to:', data.channel);
});
```

### HTTP Endpoints

**GET `/live-dashboard`**
- Returns live dashboard HTML page
- Requires authentication

**GET `/live-logs`**
- Returns live log tail HTML page
- Requires authentication

**GET `/api/realtime/metrics`**
- Returns current real-time metrics as JSON
- Public endpoint

**POST `/api/realtime/publish`**
- Publish a log entry to real-time stream
- Used for webhook integrations
- Request body: JSON log object

Example:
```bash
curl -X POST http://localhost:5000/api/realtime/publish \
  -H "Content-Type: application/json" \
  -d '{
    "level": "ERROR",
    "message": "Database connection failed",
    "log_type": "DATABASE",
    "server": "server-1"
  }'
```

## Configuration

### Environment Variables

No additional environment variables required. Uses existing:
- `ELASTICSEARCH_HOST`
- `REDIS_HOST`
- `REDIS_PORT`

### Logstash Configuration

File: `logstash/pipeline/logstash.conf`

Key sections:
- **Input plugins:** tcp, udp, http, redis, beats, file
- **Filter plugins:** csv, json, date, mutate, geoip
- **Output plugins:** elasticsearch, redis (pub/sub)

### Docker Compose Ports

```yaml
logstash:
  ports:
    - "5045:5000"    # TCP streaming
    - "5001:5001/udp"  # UDP streaming
    - "8080:8080"    # HTTP webhook
    - "5044:5044"    # Filebeat

webapp:
  ports:
    - "5000:5000"    # Flask + WebSocket
```

## Usage Examples

### 1. Send Logs via TCP

```bash
# Send JSON log to Logstash TCP input
echo '{"level":"INFO","message":"Test log","log_type":"API"}' | nc localhost 5045
```

### 2. Send Logs via HTTP Webhook

```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-01-02T10:30:00Z",
    "level": "ERROR",
    "log_type": "API",
    "message": "Request timeout",
    "endpoint": "/api/users",
    "status_code": 504,
    "response_time_ms": 30000
  }'
```

### 3. Send Logs via Redis

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

log_entry = {
    "level": "WARNING",
    "message": "High memory usage",
    "log_type": "SYSTEM",
    "server": "server-3"
}

# Publish to Redis
r.publish('logs', json.dumps(log_entry))
```

### 4. Configure Filebeat

Create `filebeat.yml`:

```yaml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/app/*.log
    json.keys_under_root: true
    json.add_error_key: true

output.logstash:
  hosts: ["localhost:5044"]
```

### 5. Using the Live Dashboard

1. Navigate to: `http://localhost:5000/live-dashboard`
2. Click "Enable Notifications" to allow desktop alerts
3. Charts will automatically update as logs arrive
4. Toggle sound on/off as needed
5. Monitor real-time metrics at the top

### 6. Using Live Log Tail

1. Navigate to: `http://localhost:5000/live-logs`
2. Use filters to narrow down logs
3. Press **Space** to pause/resume stream
4. Press **Ctrl+F** to search
5. Click "Auto-scroll: OFF" to review older logs
6. Press **Ctrl+C** to clear screen

## Performance Optimization

### Client-Side

1. **Chart Animation:** Use `'none'` mode for updates to avoid lag
2. **Buffer Limit:** Max 1000 logs in memory (circular buffer)
3. **Debouncing:** Filters applied with minimal re-renders
4. **Lazy Rendering:** Only visible logs are rendered

### Server-Side

1. **Async Mode:** eventlet for non-blocking I/O
2. **Client Filters:** Apply filters server-side before emit
3. **Thread Safety:** Proper locking for shared state
4. **Connection Pooling:** Reuse Elasticsearch/Redis connections

### Logstash

1. **Pipeline Workers:** Auto-configured based on CPU cores
2. **Batch Size:** Optimized for throughput vs. latency
3. **Queue Type:** Memory queue for low latency
4. **Filter Optimization:** Minimize regex operations

## Monitoring

### Health Checks

```bash
# Check WebSocket connection
curl http://localhost:5000/api/realtime/metrics

# Check Logstash health
curl http://localhost:9600/_node/stats

# Check Redis
redis-cli ping
```

### Metrics to Monitor

1. **Connected WebSocket Clients**
   - Track in: `/api/realtime/metrics`
   - Alert if: Unexpected drops

2. **Logs Per Second**
   - Track in: Live dashboard
   - Alert if: Drops to 0 or spikes abnormally

3. **Errors Per Minute**
   - Track in: Live dashboard
   - Alert if: Exceeds threshold (e.g., 10)

4. **WebSocket Reconnects**
   - Track in: Browser console
   - Alert if: Frequent reconnections

## Troubleshooting

### WebSocket Connection Fails

**Symptoms:** "Disconnected" status, no logs appearing

**Solutions:**
1. Check Flask app is running: `curl http://localhost:5000/api/health`
2. Verify no firewall blocking WebSocket
3. Check browser console for errors
4. Try polling transport: Add `transports: ['polling']` in Socket.IO config

### Logs Not Appearing in Real-Time

**Symptoms:** Dashboard shows 0 logs/second

**Solutions:**
1. Verify log simulation is enabled (for testing)
2. Check Redis Pub/Sub: `redis-cli SUBSCRIBE logs`
3. Verify Logstash output to Redis is configured
4. Check Elasticsearch has recent logs: `curl http://localhost:9200/saas-logs-*/_count`

### High Latency (>1 second)

**Symptoms:** Delay between log generation and display

**Solutions:**
1. Check Logstash pipeline delay
2. Reduce Elasticsearch bulk size
3. Optimize filter expressions
4. Increase Logstash workers
5. Use Redis Pub/Sub instead of Elasticsearch polling

### Memory Issues

**Symptoms:** Browser becomes slow, high memory usage

**Solutions:**
1. Verify circular buffer is working (max 1000 logs)
2. Clear logs periodically: Press Ctrl+C in Live Logs
3. Close unused WebSocket connections
4. Reduce chart data retention window

### Desktop Notifications Not Working

**Symptoms:** No notification popups

**Solutions:**
1. Check browser notification permission: `Notification.permission`
2. Click "Enable Notifications" button
3. Verify browser supports notifications
4. Check OS notification settings

## Production Deployment

### Recommended Configuration

1. **Disable Log Simulation**
   ```python
   # In app.py, comment out:
   # simulation_thread = threading.Thread(target=simulate_realtime_logs, daemon=True)
   # simulation_thread.start()
   ```

2. **Enable Redis Pub/Sub Listener**
   ```python
   # In app.py, uncomment:
   redis_thread = threading.Thread(target=listen_to_redis_pubsub, daemon=True)
   redis_thread.start()
   ```

3. **Use Production ASGI Server**
   ```bash
   gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
   ```

4. **Configure SSL/TLS for WebSocket**
   ```python
   socketio = SocketIO(app, cors_allowed_origins="*", 
                      async_mode='eventlet',
                      ssl_context=('cert.pem', 'key.pem'))
   ```

5. **Set Resource Limits**
   ```yaml
   # docker-compose.yml
   webapp:
     deploy:
       resources:
         limits:
           cpus: '2'
           memory: 2G
   ```

### Security Considerations

1. **Authentication:** All real-time endpoints require login
2. **CORS:** Configure `cors_allowed_origins` to specific domains
3. **Rate Limiting:** Implement per-client rate limits
4. **Input Validation:** Sanitize all log inputs
5. **WebSocket Authentication:** Implement token-based auth

### Scaling

**Horizontal Scaling:**
- Use Redis as message broker
- Deploy multiple Flask instances behind load balancer
- Sticky sessions for WebSocket connections

**Vertical Scaling:**
- Increase Logstash workers
- Scale Elasticsearch cluster
- Optimize Redis memory

## Integration Examples

### Python Application

```python
import socket
import json

def send_log(level, message):
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        "log_type": "APP"
    }
    
    # Send via TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 5045))
    s.send(json.dumps(log).encode() + b'\n')
    s.close()

send_log("INFO", "Application started")
```

### Node.js Application

```javascript
const net = require('net');

function sendLog(level, message) {
    const log = {
        timestamp: new Date().toISOString(),
        level: level,
        message: message,
        log_type: 'APP'
    };
    
    const client = net.connect({port: 5045}, () => {
        client.write(JSON.stringify(log) + '\n');
        client.end();
    });
}

sendLog('INFO', 'Application started');
```

### cURL (HTTP Webhook)

```bash
#!/bin/bash
send_log() {
    curl -X POST http://localhost:8080 \
      -H "Content-Type: application/json" \
      -d "{
        \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
        \"level\": \"$1\",
        \"message\": \"$2\",
        \"log_type\": \"SCRIPT\"
      }"
}

send_log "INFO" "Backup completed successfully"
```

## Testing

### Manual Testing

1. **Start the stack:**
   ```bash
   docker-compose up -d
   ```

2. **Access live dashboard:**
   - URL: http://localhost:5000/live-dashboard
   - Login if required
   - Verify logs are streaming (simulation mode)

3. **Test filters:**
   - Select "ERROR" in level filter
   - Verify only errors are displayed

4. **Test notifications:**
   - Click "Enable Notifications"
   - Wait for ERROR log
   - Verify desktop notification appears

5. **Test live logs page:**
   - URL: http://localhost:5000/live-logs
   - Press Space to pause
   - Press Space again to resume
   - Search for keyword
   - Verify highlighting

### Automated Testing

```python
# test_websocket.py
import socketio

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Connected to server')
    sio.emit('subscribe', {'channel': 'all'})

@sio.on('new_log')
def on_new_log(data):
    print(f"Received log: {data['level']} - {data['message']}")

@sio.on('metrics_update')
def on_metrics(data):
    print(f"Metrics: {data}")

sio.connect('http://localhost:5000')
sio.wait()
```

## Future Enhancements

1. **Advanced Filtering:**
   - Regular expression support
   - Boolean operators (AND, OR, NOT)
   - Saved filter presets

2. **Export Capabilities:**
   - Export filtered logs to CSV/JSON
   - Share live dashboard link with specific filters

3. **Custom Alerts:**
   - User-defined alert rules
   - Email/Slack notifications
   - Alert thresholds per metric

4. **Dashboard Customization:**
   - Drag-and-drop chart arrangement
   - Custom chart types
   - User preferences saved to MongoDB

5. **Multi-Tenancy:**
   - Tenant-specific log streams
   - Role-based access control
   - Per-tenant dashboards

## Support

For issues or questions:
1. Check logs: `docker-compose logs webapp`
2. Review browser console for client-side errors
3. Verify all services are healthy: `docker-compose ps`
4. Check documentation in `/docs` folder

## License

Same as parent project.

## Version

Real-Time Module v1.0.0 - January 2, 2026
