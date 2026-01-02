# Real-Time Monitoring - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Start the Services

```bash
# Navigate to project directory
cd saas-monitoring-platform

# Start all services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps
```

### Step 2: Access the Live Dashboard

Open your browser and navigate to:
```
http://localhost:5000/live-dashboard
```

**What you'll see:**
- ✅ Connection indicator (green = connected)
- 📊 Real-time metrics counters
- 📈 Streaming charts that update every second
- 📝 Recent activity feed

### Step 3: Enable Desktop Notifications

1. Click **"Enable Notifications"** button
2. Allow notifications when browser prompts
3. Notifications will appear for ERROR and CRITICAL logs

### Step 4: Try the Live Log Tail

Navigate to:
```
http://localhost:5000/live-logs
```

**Terminal-style interface:**
- Logs appear instantly as they arrive
- Color-coded by severity
- Press **Space** to pause/resume
- Press **Ctrl+F** to search

## 📡 Send Your First Real-Time Log

### Option 1: HTTP Webhook (Easiest)

```bash
curl -X POST http://localhost:5000/api/realtime/publish \
  -H "Content-Type: application/json" \
  -d '{
    "level": "ERROR",
    "message": "Test error message",
    "log_type": "API",
    "endpoint": "/api/test",
    "status_code": 500
  }'
```

Watch the log appear instantly in both dashboards!

**Note:** Use port 5000 (Flask app) for real-time logs. Port 8080 is for Logstash integration.

### Option 2: TCP Socket

```bash
echo '{"level":"WARNING","message":"High CPU usage","log_type":"SYSTEM"}' | nc localhost 5045
```

### Option 3: Redis Pub/Sub

```bash
redis-cli -h localhost -p 6379 PUBLISH logs '{"level":"INFO","message":"User logged in","log_type":"AUTH"}'
```

### Option 4: Python Script

```python
import requests
import json

log = {
    "level": "CRITICAL",
    "message": "Database connection lost",
    "log_type": "DATABASE"
}

response = requests.post(
    'http://localhost:8080',
    json=log
)
print(f"Status: {response.status_code}")
```

## 🎮 Interactive Features

### Live Dashboard

**Metrics Displayed:**
- 📊 Logs Per Second - Current throughput
- ⚠️ Errors Per Minute - Error rate
- 👥 Connected Users - Active WebSocket connections
- 📈 Total Processed - Cumulative count

**Charts:**
1. **Log Stream Rate** - Real-time line chart (60-second rolling window)
2. **Log Levels** - Doughnut chart showing distribution
3. **Response Time** - Bar chart with latency buckets
4. **Status Codes** - Top HTTP status codes

### Live Logs (Tail -f Mode)

**Keyboard Shortcuts:**
```
Space        Pause/Resume log stream
Ctrl+C       Clear all logs
Ctrl+S       Toggle auto-scroll
Ctrl+F       Focus search box
```

**Filters:**
- **Log Level:** Filter by INFO, DEBUG, WARNING, ERROR, CRITICAL
- **Service Type:** Filter by API, DATABASE, AUTH, SYSTEM
- **Search:** Text search with yellow highlighting

**Features:**
- ✅ Auto-scroll (follows newest logs)
- ✅ Manual scroll detection (disables auto-scroll when you scroll up)
- ✅ Circular buffer (max 1000 logs to prevent memory issues)
- ✅ Real-time statistics (log count, error count, rate)

## 🔧 Configuration

### Test Mode (Default)

By default, the app generates **simulated logs** for testing:
- Random log levels
- Random endpoints and status codes
- 0.1 to 2 seconds between logs

**This is perfect for testing without setting up log sources!**

### Production Mode

To use real log sources:

1. Edit `app/app.py` and find the `start_background_threads()` function:

```python
def start_background_threads():
    # COMMENT OUT simulation (for production)
    # simulation_thread = threading.Thread(target=simulate_realtime_logs, daemon=True)
    # simulation_thread.start()
    
    # UNCOMMENT Redis listener (for production)
    redis_thread = threading.Thread(target=listen_to_redis_pubsub, daemon=True)
    redis_thread.start()
```

2. Rebuild and restart:
```bash
docker-compose down
docker-compose up -d --build
```

## 📨 Streaming Input Ports

| Port | Service | Protocol | Purpose |
|------|---------|----------|---------|
| 5000 | Flask | HTTP | Real-time API (use `/api/realtime/publish`) |
| 5045 | Logstash | TCP | High-throughput streaming |
| 5001 | Logstash | UDP | Low-latency, fire-and-forget |
| 8080 | Logstash | HTTP | Logstash HTTP input |
| 5044 | Logstash | Beats | Filebeat log tailing |

**For real-time dashboard logs: Use Flask on port 5000 with `/api/realtime/publish` endpoint**

## 🧪 Testing Scenarios

### Scenario 1: High Error Rate Alert

```bash
# Send multiple errors rapidly
for i in {1..20}; do
  curl -X POST http://localhost:5000/api/realtime/publish \
    -H "Content-Type: application/json" \
    -d "{\"level\":\"ERROR\",\"message\":\"Error $i\"}"
  sleep 0.1
done
```

**Expected:**
- Desktop notifications
- Red navbar flash
- Error counter increases
- Alert badge appears

### Scenario 2: Different Log Levels

```bash
# Send mixed log levels
curl -X POST http://localhost:5000/api/realtime/publish -H "Content-Type: application/json" \
  -d '{"level":"INFO","message":"Application started"}'

curl -X POST http://localhost:5000/api/realtime/publish -H "Content-Type: application/json" \
  -d '{"level":"DEBUG","message":"Debug information"}'

curl -X POST http://localhost:5000/api/realtime/publish -H "Content-Type: application/json" \
  -d '{"level":"WARNING","message":"Low disk space"}'

curl -X POST http://localhost:5000/api/realtime/publish -H "Content-Type: application/json" \
  -d '{"level":"CRITICAL","message":"System failure"}'
```

**Expected:**
- Doughnut chart updates
- Different colors in live logs
- CRITICAL logs pulse with animation

### Scenario 3: Filtering

1. Go to `/live-logs`
2. Select "ERROR" from Level Filter
3. Send mixed logs (as in Scenario 2)
4. **Expected:** Only ERROR logs display

### Scenario 4: Search Highlighting

1. Go to `/live-logs`
2. Type "database" in search box
3. Send logs with "database" keyword
4. **Expected:** Keyword highlighted in yellow

## 🐛 Troubleshooting

### No Logs Appearing?

**Check 1: Simulation is enabled**
```bash
docker-compose logs webapp | grep "Real-time processing threads started"
```

**Check 2: WebSocket is connected**
- Look for green indicator in top bar
- Browser console should show "Connected to server"

**Check 3: Services are healthy**
```bash
docker-compose ps
# All services should show "healthy"
```

### Connection Keeps Dropping?

**Check 1: Firewall/Proxy**
- WebSocket requires open connection
- Some corporate proxies block WebSockets

**Check 2: Browser compatibility**
- Use modern browser (Chrome, Firefox, Edge)
- Check browser console for errors

**Check 3: Try polling mode**
Edit `live_dashboard.html` and `live_logs.html`:
```javascript
socket = io(wsUrl, {
    transports: ['polling'],  // Force polling instead of WebSocket
    // ... rest of config
});
```

### Desktop Notifications Not Working?

**Check 1: Browser permission**
- Browser settings → Notifications → Allow for localhost
- Or click "Enable Notifications" button

**Check 2: Operating system**
- Windows: Check notification settings
- Mac: System Preferences → Notifications
- Linux: Varies by distro

**Check 3: HTTPS requirement**
- Some browsers require HTTPS for notifications
- Use HTTPS in production

### High CPU Usage?

**Solution 1: Reduce log simulation rate**
Edit `app.py` `simulate_realtime_logs()`:
```python
time.sleep(random.uniform(1, 5))  # Increase from (0.1, 2)
```

**Solution 2: Reduce chart update frequency**
Edit `live_dashboard.html`:
```javascript
realtime: {
    duration: 60000,
    refresh: 2000,  // Increase from 1000 (1 second to 2 seconds)
    delay: 2000
}
```

## 📊 Performance Benchmarks

**Expected Performance:**
- **Latency:** <500ms from log generation to display
- **Throughput:** 1000+ logs/second
- **Memory:** ~50MB per 1000 logs in browser
- **CPU:** ~10% for real-time processing

**Optimization Tips:**
1. Use circular buffer (already implemented)
2. Limit chart data points (60-second window)
3. Disable animations for high-volume scenarios
4. Use filters to reduce displayed logs

## 🎯 Common Use Cases

### Use Case 1: Application Monitoring

Monitor your application in real-time:
```python
# In your application
import logging
import socket
import json

def send_to_monitor(level, message):
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        "log_type": "APP"
    }
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('monitor-host', 5045))
    s.send(json.dumps(log).encode() + b'\n')
    s.close()

# Use in your app
send_to_monitor("ERROR", "Payment processing failed")
```

### Use Case 2: DevOps Team Dashboard

Display on big screen in office:
1. Open `/live-dashboard` on large monitor
2. Enable auto-refresh
3. Team can see real-time system health
4. Instant visibility into errors and performance

### Use Case 3: Incident Response

When investigating an issue:
1. Open `/live-logs`
2. Filter by ERROR level
3. Filter by affected service
4. Search for relevant keywords
5. Pause stream to analyze
6. Copy log details for troubleshooting

### Use Case 4: Load Testing

During load tests:
1. Monitor Logs Per Second metric
2. Watch Response Time chart
3. Check for errors during peak load
4. Verify system handles throughput

## 🔐 Security Notes

**In Production:**
1. Enable authentication on all endpoints
2. Use HTTPS/WSS for encrypted connections
3. Implement rate limiting
4. Restrict CORS origins
5. Validate all log inputs

**Current Setup:**
- Authentication required for web pages
- WebSocket uses session-based auth
- HTTP webhook (port 8080) is open (for testing)

## 📚 Next Steps

1. **Read Full Documentation:**
   - `/docs/REALTIME_MODULE.md` - Complete feature guide

2. **Integrate Your Application:**
   - Send logs via HTTP, TCP, or Redis
   - See integration examples in documentation

3. **Customize Dashboards:**
   - Modify chart types
   - Adjust metrics displayed
   - Change color schemes

4. **Set Up Alerts:**
   - Configure notification rules
   - Add email/Slack integration
   - Set custom thresholds

## 💡 Tips & Tricks

1. **Keep Live Logs Tab Open:**
   - Acts as a persistent log viewer
   - Useful during development

2. **Use Search Effectively:**
   - Search for user IDs, IPs, or error codes
   - Combine with filters for precision

3. **Monitor Multiple Services:**
   - Open multiple browser tabs
   - Each can have different filters

4. **Keyboard Shortcuts:**
   - Learn shortcuts for faster workflow
   - Space bar is your friend (pause/resume)

5. **Share Insights:**
   - Take screenshots of charts
   - Export filtered logs
   - Share dashboard URL with team

## ✅ Verification Checklist

Before moving to production, verify:

- [ ] WebSocket connects successfully
- [ ] Logs appear in real-time (<1 second)
- [ ] Charts update smoothly
- [ ] Filters work correctly
- [ ] Desktop notifications appear
- [ ] Pause/Resume functions properly
- [ ] Auto-scroll behaves as expected
- [ ] Search highlighting works
- [ ] Memory usage is stable
- [ ] Can handle expected log volume

## 🎉 You're All Set!

The real-time monitoring module is now ready to use. Start sending logs and watch them appear instantly!

**Questions?** Check `/docs/REALTIME_MODULE.md` for detailed documentation.

**Happy Monitoring! 📊🚀**
