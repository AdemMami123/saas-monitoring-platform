# Search Functionality - Complete Implementation Guide

## Overview
A comprehensive search page has been implemented with advanced filtering, sorting, pagination, and export capabilities for searching application logs stored in Elasticsearch.

## Backend Implementation (app/app.py)

### 1. `/api/search` Endpoint (POST)
**Location:** Line ~227

**Purpose:** Comprehensive search with all filters and pagination

**Parameters (JSON POST body):**
```json
{
  "q": "search query",           // Search in message, endpoint, user_agent
  "level": "INFO",                // Log level filter (ALL, DEBUG, INFO, WARNING, ERROR, CRITICAL)
  "date_from": "2025-10-01",      // Date range start
  "date_to": "2025-11-01",        // Date range end
  "endpoint": "/api/users",       // Specific endpoint filter
  "status_code": "2xx",           // Status code filter (2xx, 4xx, 5xx, or specific like 200)
  "server": "server-01",          // Server filter (server-01 to server-05)
  "page": 1,                      // Current page (default: 1)
  "per_page": 50,                 // Results per page (default: 50)
  "sort_field": "timestamp",      // Sort field (timestamp, level, endpoint, status_code, response_time_ms)
  "sort_order": "desc"            // Sort order (asc, desc)
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "_id": "abc123",
      "timestamp": "2025-11-01T10:30:00Z",
      "level": "INFO",
      "endpoint": "/api/users",
      "method": "GET",
      "status_code": 200,
      "response_time_ms": 145,
      "client_ip": "192.168.1.100",
      "user_id": 42,
      "server": "server-01",
      "tenant_id": "tenant_5",
      "message": "Successfully processed GET request to /api/users",
      "user_agent": "Mozilla/5.0...",
      "sql_query": null,
      "query_duration_ms": null
    }
  ],
  "total": 12345,
  "page": 1,
  "pages": 247,
  "per_page": 50
}
```

**Query Building Logic:**
1. **Text Search:** Multi-match query on `message`, `endpoint`, `user_agent` fields
2. **Log Level:** Exact term match on `level.keyword`
3. **Date Range:** Range filter on `timestamp` field
4. **Endpoint:** Exact term match on `endpoint.keyword`
5. **Status Code:** 
   - `2xx`: Range 200-299
   - `4xx`: Range 400-499
   - `5xx`: Range 500-599
   - Specific: Exact match (e.g., 200)
6. **Server:** Exact term match on `server.keyword`
7. **Sorting:** Dynamic sorting on specified field
8. **Pagination:** `from` and `size` parameters

### 2. `/api/search/endpoints` Endpoint (GET)
**Location:** Line ~375

**Purpose:** Get unique endpoints for filter dropdown

**Response:**
```json
{
  "success": true,
  "endpoints": [
    "/api/auth/login",
    "/api/users",
    "/api/orders",
    "/api/products",
    "/api/analytics/dashboard"
  ]
}
```

**Implementation:** Uses Elasticsearch aggregation to get unique endpoint values

### 3. `/search` Route (GET)
**Location:** Line ~115

**Purpose:** Render search page template

**Returns:** `search.html` template

## Frontend Implementation (app/templates/search.html)

### Page Structure

#### 1. **Navbar**
- Dashboard link: `/`
- Upload link: `/upload`
- **Search link (active): `/search`**

#### 2. **Search Section**
Components:
- **Main Search Input:**
  - Large search box with icon
  - Placeholder: "Search in messages, endpoints, user agents..."
  - Enter key support for quick search

- **Advanced Filters (Collapsible):**
  - Toggle button: Shows/hides advanced filters
  - Filters include:
    * **Log Level Dropdown:** ALL, DEBUG, INFO, WARNING, ERROR, CRITICAL
    * **Date From:** Datetime-local input
    * **Date To:** Datetime-local input
    * **Endpoint Dropdown:** Dynamically loaded from ES
    * **Status Code Dropdown:** 2xx, 4xx, 5xx, specific codes
    * **Server Dropdown:** server-01 to server-05
    * **Results Per Page:** 25, 50, 100, 200

- **Action Buttons:**
  - **Search Button (Primary):** Executes search
  - **Reset Button:** Clears all filters and results

#### 3. **Results Section**

**Results Header:**
- Title: "Search Results"
- Results count info: "Showing 1-50 of 12,345 results"
- Export to CSV button (enabled when results exist)

**Results Table:**
Columns:
1. **Timestamp** - Formatted: "Oct 29, 10:30 AM"
2. **Level** - Color-coded badge (INFO/WARNING/ERROR/CRITICAL)
3. **Endpoint** - Code-formatted
4. **Status** - Color-coded by range (2xx green, 4xx orange, 5xx red)
5. **Response Time** - Color-coded by speed (fast/medium/slow)
6. **Message** - Truncated to 100 chars with full text in tooltip
7. **Actions** - View Details button

**Table Features:**
- Sortable columns (click header to sort)
- Sort indicators (up/down chevrons)
- Hover effects on rows
- Loading overlay during search
- Empty state when no results
- Initial state before first search

**Pagination:**
- Previous/Next buttons
- Page numbers (max 10 visible)
- Active page highlighted
- Disabled state for boundary pages
- Click handler for page navigation
- Smooth scroll to top on page change

#### 4. **Log Details Modal**
Triggered by "View Details" button

**Displays:**
- Full timestamp
- Level badge
- Endpoint and method
- Status code
- Response time
- Client IP
- User ID (or "Anonymous")
- Server
- Tenant ID
- Full message (not truncated)
- User agent
- SQL query (if present) with duration

### JavaScript Features

#### State Management
```javascript
let currentPage = 1;
let currentSort = { field: 'timestamp', order: 'desc' };
let currentFilters = {};
let searchResults = null;
```

#### Key Functions

**1. `performSearch()`**
- Gathers all filter values
- Shows loading overlay
- Makes POST request to `/api/search`
- Handles response and errors
- Calls render functions

**2. `renderResults(data)`**
- Clears existing results
- Creates table rows for each log
- Formats timestamps, badges, status codes
- Adds color coding
- Truncates messages
- Adds view details buttons

**3. `renderPagination(data)`**
- Builds pagination UI
- Shows max 10 page numbers
- Adds previous/next buttons
- Handles disabled states
- Attaches click handlers

**4. `updateResultsInfo(data)`**
- Updates "Showing X-Y of Z results" text

**5. `viewDetails(logId)`**
- Finds log in results array
- Populates modal with full details
- Shows modal

**6. `exportToCSV()`**
- Creates CSV content from current results
- Generates downloadable file
- Filename: `logs_export_YYYY-MM-DD.csv`

**7. `loadEndpoints()`**
- Fetches unique endpoints from API
- Populates endpoint filter dropdown
- Called on page load

#### Event Handlers

**Search Actions:**
- Search button click → `performSearch()`
- Enter key in search input → `performSearch()`
- Reset button → Clear all filters and reset UI

**Filter Actions:**
- Toggle filters button → Show/hide advanced filters

**Sorting:**
- Click sortable header → Toggle sort order, update icon, perform search

**Pagination:**
- Click page link → Update page, perform search, scroll to top

**Export:**
- Click export button → Generate and download CSV

### CSS Styling

**Color Coding:**
```css
/* Log Levels */
.badge-INFO { background: #0dcaf0; }
.badge-WARNING { background: #ffc107; color: #000; }
.badge-ERROR { background: #dc3545; }
.badge-CRITICAL { background: #6f42c1; }

/* Status Codes */
.status-2xx { color: #198754; } /* Green */
.status-4xx { color: #fd7e14; } /* Orange */
.status-5xx { color: #dc3545; } /* Red */

/* Response Times */
.response-fast { color: #198754; }   /* < 500ms */
.response-medium { color: #ffc107; } /* 500-2000ms */
.response-slow { color: #dc3545; }   /* > 2000ms */
```

**Interactive Elements:**
- Sortable headers with hover effect
- Loading overlay with spinner
- Smooth transitions
- Responsive table

## Usage Examples

### Basic Search
1. Enter search term: "login"
2. Click "Search"
3. View results

### Advanced Search with Filters
1. Click "Advanced Filters"
2. Select Level: "ERROR"
3. Select Status Code: "5xx"
4. Select Date range
5. Click "Search"

### Sorting Results
1. Perform a search
2. Click "Response Time" column header
3. Results sorted by response time (ascending)
4. Click again to reverse order

### Viewing Details
1. In results table, click "View Details" (eye icon)
2. Modal opens with complete log information
3. Review all fields including SQL queries

### Exporting Results
1. Perform a search
2. Click "Export to CSV" button
3. CSV file downloads with current page results

### Pagination
1. Perform search with many results
2. Pagination appears at bottom
3. Click page numbers or Next/Previous
4. Results update for selected page

## API Integration

### Elasticsearch Index Mapping
Expected fields in `saas-logs-*` indices:
- `timestamp` (date)
- `level` (keyword)
- `endpoint` (text + keyword)
- `method` (keyword)
- `status_code` (integer)
- `response_time_ms` (integer)
- `client_ip` (ip)
- `user_id` (integer)
- `server` (keyword)
- `tenant_id` (keyword)
- `message` (text)
- `user_agent` (text)
- `sql_query` (text, optional)
- `query_duration_ms` (integer, optional)

### Error Handling

**Backend Errors:**
- Elasticsearch unavailable → 503 error
- Invalid parameters → 400 error
- Query execution error → 500 error with message

**Frontend Errors:**
- Network error → Display error message in table
- No results → Show empty state
- API error → Display error message

## Performance Considerations

1. **Pagination:** Limits results to 50 per page by default
2. **Index Wildcards:** Uses `saas-logs-*` pattern for flexibility
3. **Field Selection:** Returns all fields (no projection for completeness)
4. **Aggregations:** Endpoints aggregation limited to 100 unique values
5. **Export Limit:** Current page only (not all results)

## Future Enhancements

- [ ] Real-time search (as-you-type)
- [ ] Saved search queries
- [ ] Search history
- [ ] Export all results (not just current page)
- [ ] Advanced query builder
- [ ] Date range presets (Last 24h, Last 7 days, etc.)
- [ ] Column visibility toggle
- [ ] Custom column ordering
- [ ] Bulk export with background job
- [ ] Search result highlighting
- [ ] Regex search support
- [ ] Field-specific search syntax

## Testing

### Manual Test Steps

1. **Access Search Page:**
   ```
   http://localhost:5000/search
   ```

2. **Test Basic Search:**
   - Enter "login" in search box
   - Click "Search"
   - Verify results appear

3. **Test Filters:**
   - Click "Advanced Filters"
   - Select Level: "ERROR"
   - Click "Search"
   - Verify only ERROR logs appear

4. **Test Sorting:**
   - Click "Response Time" header
   - Verify results sorted
   - Click again to reverse

5. **Test Pagination:**
   - Perform search with many results
   - Click "Next" button
   - Verify page 2 loads

6. **Test Details Modal:**
   - Click eye icon on any result
   - Verify modal shows all fields
   - Close modal

7. **Test Export:**
   - Click "Export to CSV"
   - Verify file downloads
   - Open CSV and check content

## Summary

✅ **Comprehensive search endpoint** with all filters
✅ **Advanced filtering** (level, dates, endpoint, status, server)
✅ **Full-text search** in multiple fields
✅ **Sortable columns** with visual indicators
✅ **Pagination** with page numbers and navigation
✅ **Details modal** with complete log information
✅ **Export to CSV** functionality
✅ **Responsive design** with Bootstrap 5
✅ **Loading states** and error handling
✅ **Color-coded badges** for quick identification
✅ **Empty states** for better UX

The search functionality is production-ready and fully operational!
