# Kibana Setup Guide

Complete step-by-step instructions for setting up visualizations in Kibana for the SaaS Monitoring Platform.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Accessing Kibana](#accessing-kibana)
- [Creating Index Pattern](#creating-index-pattern)
- [Visualization 1: Response Time Line Chart](#visualization-1-response-time-line-chart)
- [Visualization 2: Status Code Pie Chart](#visualization-2-status-code-pie-chart)
- [Visualization 3: Top Endpoints Bar Chart](#visualization-3-top-endpoints-bar-chart)
- [Visualization 4: Error Rate Timeline](#visualization-4-error-rate-timeline)
- [Visualization 5: Slowest Queries Table](#visualization-5-slowest-queries-table)
- [Creating a Dashboard](#creating-a-dashboard)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure:
1. Docker containers are running: `docker-compose up -d`
2. Elasticsearch is healthy: Check at http://localhost:9200
3. Kibana is accessible: http://localhost:5601
4. Log data has been ingested via Logstash

## Accessing Kibana

1. Open your web browser
2. Navigate to: **http://localhost:5601**
3. Wait for Kibana to fully load (may take 30-60 seconds on first startup)

---

## Creating Index Pattern

Before creating visualizations, you need to create an index pattern to tell Kibana which Elasticsearch indices to use.

### Steps:

1. **Navigate to Stack Management**
   - Click the hamburger menu (☰) in the top-left corner
   - Scroll down and click **"Stack Management"**
   - In the left sidebar, under "Kibana", click **"Index Patterns"**

2. **Create Index Pattern**
   - Click the **"Create index pattern"** button
   - In the "Index pattern name" field, enter: `saas-logs-*`
   - This pattern matches all indices starting with "saas-logs-"
   - Click **"Next step"**

3. **Configure Time Field**
   - In the "Time field" dropdown, select: **@timestamp**
   - This tells Kibana which field to use for time-based queries
   - Click **"Create index pattern"**

4. **Verify Creation**
   - You should see your index pattern listed
   - Note the number of fields detected (should be 15-20+)

---

## Visualization 1: Response Time Line Chart

This visualization shows average response times over time, helping identify performance trends and spikes.

### Steps:

1. **Navigate to Visualize**
   - Click the hamburger menu (☰)
   - Click **"Visualize Library"**
   - Click **"Create visualization"** button

2. **Select Visualization Type**
   - Choose **"Line"** from the visualization types
   - Select your index pattern: **saas-logs-***

3. **Configure Time Range**
   - In the top-right corner, click the time picker
   - Select **"Last 7 days"** or your preferred range
   - Click **"Apply"**

4. **Configure Metrics (Y-axis)**
   - In the right panel under "Metrics"
   - Click on **"Count"** to expand
   - Change aggregation to **"Average"**
   - In the "Field" dropdown, select: **response_time** or **response_time_ms**
   - In the "Custom label" field, enter: `Average Response Time (ms)`

5. **Configure Buckets (X-axis)**
   - Click **"Add"** under "Buckets"
   - Select **"X-axis"**
   - Aggregation: Select **"Date Histogram"**
   - Field: Select **@timestamp**
   - Minimum interval: Choose **"Auto"** or **"1h"** for hourly data
   - Custom label: `Time`

6. **Apply and Save**
   - Click the **"Update"** button (play icon) to see the chart
   - Click **"Save"** in the top menu
   - Title: `Response Time Over Time`
   - Description: `Average response time trending`
   - Click **"Save"**

### Expected Result:
A line chart showing response time trends over time, with time on X-axis and average response time (ms) on Y-axis.

---

## Visualization 2: Status Code Pie Chart

This visualization shows the distribution of HTTP status codes, making it easy to spot error rates.

### Steps:

1. **Create New Visualization**
   - In Visualize Library, click **"Create visualization"**
   - Select **"Pie"**
   - Select index pattern: **saas-logs-***

2. **Configure Metrics**
   - Metrics should default to **"Count"**
   - Custom label: `Log Count`

3. **Configure Buckets - Slices**
   - Click **"Add"** under "Buckets"
   - Select **"Split slices"**
   - Aggregation: **"Terms"**
   - Field: **status_code.keyword** (or just **status_code**)
   - Order by: **"Metric: Count"**
   - Order: **"Descending"**
   - Size: **10** (show top 10 status codes)
   - Custom label: `Status Code`

4. **Customize Appearance**
   - Click on "Options" tab at the top
   - Enable **"Show labels"** to display status codes on slices
   - Enable **"Show values"** to display counts

5. **Apply Colors (Optional)**
   - You can manually assign colors to status codes:
     - 200-299: Green (success)
     - 400-499: Yellow (client errors)
     - 500-599: Red (server errors)

6. **Save Visualization**
   - Click **"Update"** to preview
   - Click **"Save"**
   - Title: `Status Code Distribution`
   - Description: `HTTP status code breakdown`
   - Click **"Save"**

### Expected Result:
A pie chart showing the percentage distribution of different HTTP status codes.

---

## Visualization 3: Top Endpoints Bar Chart

This visualization identifies the most frequently accessed API endpoints.

### Steps:

1. **Create New Visualization**
   - Click **"Create visualization"**
   - Select **"Bar"** (Vertical Bar)
   - Select index pattern: **saas-logs-***

2. **Configure Metrics (Y-axis)**
   - Metrics: **"Count"**
   - Custom label: `Request Count`

3. **Configure Buckets (X-axis)**
   - Click **"Add"** under "Buckets"
   - Select **"X-axis"**
   - Aggregation: **"Terms"**
   - Field: **endpoint.keyword** (or **endpoint**)
   - Order by: **"Metric: Count"**
   - Order: **"Descending"**
   - Size: **15** (show top 15 endpoints)
   - Custom label: `Endpoint`

4. **Format Options**
   - In "Metrics & axes" tab:
   - Check **"Show values on chart"**
   - Y-axis: Position: **Left**
   - X-axis: You may want to rotate labels for readability

5. **Apply and Save**
   - Click **"Update"**
   - Click **"Save"**
   - Title: `Top 15 Endpoints by Request Count`
   - Description: `Most frequently accessed API endpoints`
   - Click **"Save"**

### Expected Result:
A bar chart showing the most accessed endpoints, sorted by request count in descending order.

---

## Visualization 4: Error Rate Timeline

This visualization tracks error occurrences over time, helping you identify when issues occur.

### Steps:

1. **Create New Visualization**
   - Click **"Create visualization"**
   - Select **"Area"** (or "Line" for similar effect)
   - Select index pattern: **saas-logs-***

2. **Configure Metrics (Y-axis)**
   - Metrics: **"Count"**
   - Custom label: `Error Count`

3. **Add Filter for Errors**
   - Click **"Add filter"** at the top
   - Click **"Edit as Query DSL"** for advanced filtering
   - Enter the following query:
     ```json
     {
       "bool": {
         "should": [
           {"term": {"level.keyword": "ERROR"}},
           {"term": {"level.keyword": "CRITICAL"}},
           {"range": {"status_code": {"gte": 400}}}
         ],
         "minimum_should_match": 1
       }
     }
     ```
   - Or use simple KQL: `level:ERROR OR level:CRITICAL OR status_code >= 400`
   - Label: `Errors Only`
   - Click **"Save"**

4. **Configure Buckets (X-axis)**
   - Click **"Add"** under "Buckets"
   - Select **"X-axis"**
   - Aggregation: **"Date Histogram"**
   - Field: **@timestamp**
   - Minimum interval: **"1h"** or **"Auto"**
   - Custom label: `Time`

5. **Add Split Series (Optional)**
   - Click **"Add"** under "Buckets"
   - Select **"Split series"**
   - Sub-aggregation: **"Terms"**
   - Field: **level.keyword** or **status_code.keyword**
   - Order by: **"Metric: Count"**
   - Size: **5**
   - This will show different error types as different colored areas

6. **Apply and Save**
   - Click **"Update"**
   - Click **"Save"**
   - Title: `Error Rate Over Time`
   - Description: `Timeline of errors and critical issues`
   - Click **"Save"**

### Expected Result:
An area chart showing error occurrences over time, potentially split by error type or severity.

---

## Visualization 5: Slowest Queries Table

This visualization identifies the slowest performing requests, helping optimize performance.

### Steps:

1. **Create New Visualization**
   - Click **"Create visualization"**
   - Select **"Data Table"** (or use newer "Table" type)
   - Select index pattern: **saas-logs-***

2. **Configure Metrics**
   - Click **"Add"** under Metrics
   - Add multiple metric columns:
   
   **Metric 1: Max Response Time**
   - Aggregation: **"Max"**
   - Field: **response_time** or **response_time_ms**
   - Custom label: `Max Response Time (ms)`
   
   **Metric 2: Average Response Time**
   - Click **"Add metric"**
   - Aggregation: **"Average"**
   - Field: **response_time** or **response_time_ms**
   - Custom label: `Avg Response Time (ms)`
   
   **Metric 3: Request Count**
   - Click **"Add metric"**
   - Aggregation: **"Count"**
   - Custom label: `Request Count`

3. **Configure Buckets (Rows)**
   - Click **"Add"** under "Buckets"
   - Select **"Split rows"**
   - Aggregation: **"Terms"**
   - Field: **endpoint.keyword**
   - Order by: **"Metric: Max response_time"** (or your max metric)
   - Order: **"Descending"**
   - Size: **20** (show top 20 slowest endpoints)
   - Custom label: `Endpoint`

4. **Add Secondary Bucket (Optional)**
   - Click **"Add"** under "Buckets"
   - Select **"Split rows"**
   - Sub-aggregation: **"Terms"**
   - Field: **http_method.keyword** or **method.keyword**
   - Order by: **"Metric: Max response_time"**
   - Size: **5**
   - Custom label: `HTTP Method`

5. **Configure Options**
   - Click on "Options" tab
   - Enable **"Show total"**
   - Enable **"Show metrics for every bucket"**
   - Per page: **10** or **20**

6. **Apply and Save**
   - Click **"Update"**
   - Click **"Save"**
   - Title: `Slowest Endpoints Performance Table`
   - Description: `Endpoints ranked by response time`
   - Click **"Save"**

### Expected Result:
A data table showing endpoints sorted by slowest response times, with columns for max, average response times, and request counts.

---

## Creating a Dashboard

Now that you have all five visualizations, create a dashboard to view them together.

### Steps:

1. **Navigate to Dashboard**
   - Click the hamburger menu (☰)
   - Click **"Dashboard"**
   - Click **"Create dashboard"**

2. **Add Visualizations**
   - Click **"Add"** or **"Add from library"**
   - Select all five visualizations you created:
     1. Response Time Over Time
     2. Status Code Distribution
     3. Top 15 Endpoints by Request Count
     4. Error Rate Over Time
     5. Slowest Endpoints Performance Table

3. **Arrange Dashboard**
   - Drag and resize visualizations to your preferred layout
   - Suggested layout:
     ```
     +----------------------------------+----------------------------------+
     |  Response Time Over Time (Line)  |  Status Code Dist. (Pie)        |
     +----------------------------------+----------------------------------+
     |  Top Endpoints (Bar)             |  Error Rate Timeline (Area)     |
     +----------------------------------+----------------------------------+
     |  Slowest Queries Table (Full Width)                                |
     +---------------------------------------------------------------------+
     ```

4. **Configure Time Range**
   - Set dashboard-wide time range in top-right corner
   - Recommended: **"Last 7 days"**

5. **Save Dashboard**
   - Click **"Save"** in top menu
   - Title: `SaaS Monitoring Dashboard`
   - Description: `Comprehensive monitoring dashboard for SaaS application`
   - Check **"Store time with dashboard"** if you want to save current time range
   - Click **"Save"**

6. **Set as Default (Optional)**
   - Go to Stack Management → Kibana → Advanced Settings
   - Search for `defaultRoute`
   - Set to: `/app/dashboards#/view/YOUR_DASHBOARD_ID`

---

## Advanced Features

### Adding Filters to Dashboard

1. Click **"Add filter"** at the top of the dashboard
2. Examples:
   - **Filter by environment**: `environment:production`
   - **Filter by log level**: `level:ERROR`
   - **Filter by status code range**: `status_code >= 500`

### Creating Alerts (Kibana Alerting)

1. Click **"Alerts and Actions"** in Stack Management
2. Create rules for:
   - Response time exceeds threshold
   - Error rate spike
   - Specific endpoint failures

### Refresh Settings

- Click the refresh icon in top-right
- Set auto-refresh interval (e.g., 30 seconds, 1 minute)
- Useful for real-time monitoring

---

## Troubleshooting

### No Data Appears in Visualizations

**Problem**: Visualizations show "No results found"

**Solutions**:
1. Check time range - expand to "Last 30 days" or "Last year"
2. Verify data exists in Elasticsearch:
   ```bash
   curl http://localhost:9200/saas-logs-*/_count
   ```
3. Check index pattern includes your indices
4. Verify Logstash has processed uploaded files
5. Generate sample logs using `generate_logs.py` script

### Field Not Found Errors

**Problem**: Selected field doesn't appear in dropdown

**Solutions**:
1. Refresh index pattern:
   - Stack Management → Index Patterns
   - Click your pattern
   - Click refresh button (↻)
2. Check field name in Elasticsearch:
   ```bash
   curl http://localhost:9200/saas-logs-*/_mapping
   ```
3. Ensure field is not analyzed (use `.keyword` suffix for text fields)

### Visualizations Load Slowly

**Solutions**:
1. Reduce time range
2. Reduce number of buckets/terms
3. Add more specific filters
4. Increase Elasticsearch heap size in docker-compose.yml

### Cannot Create Index Pattern

**Solutions**:
1. Verify Elasticsearch is running: `docker ps`
2. Check Elasticsearch health: http://localhost:9200/_cluster/health
3. Verify indices exist: http://localhost:9200/_cat/indices
4. Restart Kibana: `docker restart saas-kibana`

### Visualizations Not Updating

**Solutions**:
1. Click refresh button manually
2. Check auto-refresh is enabled
3. Verify new data is being ingested
4. Clear browser cache

---

## Field Reference

Common fields used in SaaS logs:

| Field Name | Type | Description |
|------------|------|-------------|
| `@timestamp` | date | Log timestamp (primary time field) |
| `level` | keyword | Log level (INFO, WARNING, ERROR, etc.) |
| `status_code` | integer | HTTP status code |
| `response_time` | float | Response time in milliseconds |
| `endpoint` | keyword | API endpoint/URL path |
| `http_method` | keyword | HTTP method (GET, POST, etc.) |
| `user_id` | keyword | User identifier |
| `ip_address` | ip | Client IP address |
| `message` | text | Log message |
| `environment` | keyword | Environment (production, staging, etc.) |
| `region` | keyword | Geographic region |

---

## Next Steps

1. **Customize visualizations** - Adjust colors, labels, and formats
2. **Create more dashboards** - Separate dashboards for different teams/purposes
3. **Set up alerts** - Get notified of critical issues
4. **Export dashboards** - Share with team or backup configuration
5. **Explore Canvas** - Create more advanced, custom dashboards
6. **Set up Reporting** - Schedule PDF/PNG reports via email

---

## Additional Resources

- [Kibana Official Documentation](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Elasticsearch Query DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)
- [Kibana Lens](https://www.elastic.co/guide/en/kibana/current/lens.html) - Modern visualization builder
- [Kibana Alerting](https://www.elastic.co/guide/en/kibana/current/alerting-getting-started.html)

---

**Dashboard Creation Complete! 🎉**

Your SaaS Monitoring Platform now has comprehensive visualizations for tracking performance, errors, and system health.
