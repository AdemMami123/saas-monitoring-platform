# Quick Upload Guide

## How to Upload Log Files

### Method 1: Drag & Drop
1. Navigate to http://localhost:5000/upload
2. Drag your CSV or JSON file to the blue upload area
3. Release the file when the area highlights
4. Review file details
5. Click "Upload File" button
6. Watch the progress bar
7. Success! Your file appears in the Recent Uploads table

### Method 2: Browse Files
1. Navigate to http://localhost:5000/upload
2. Click "Browse Files" button
3. Select your file from the file picker
4. Review file details
5. Click "Upload File" button
6. Watch the progress bar
7. Success! Your file appears in the Recent Uploads table

## File Requirements

✅ **Accepted Formats:** CSV, JSON only
✅ **Maximum Size:** 100 MB
✅ **Naming:** Any valid filename (auto-renamed with timestamp)

## What Happens After Upload

1. **File Storage:** Saved to `/app/uploads/` with timestamp prefix
2. **Metadata:** Stored in MongoDB `files` collection
3. **Log Count:** Automatically calculated from file content
4. **Status:** Set to "completed" immediately
5. **Table Update:** Recent Uploads table refreshes automatically

## Managing Uploads

### View Recent Uploads
- Last 10 uploads displayed in table
- Shows: filename, date, size, log count, status
- Click "Refresh" to update the list

### Delete Upload
1. Find the file in Recent Uploads table
2. Click the trash icon (🗑️)
3. Confirm deletion
4. File removed from disk and database

## Upload Status Badges

🟢 **Completed** - File successfully uploaded and processed
🟡 **Processing** - File being processed by Logstash
🔴 **Failed** - Upload or processing error
⚪ **Pending** - Awaiting processing

## Test File Location

Use the generated test file:
```
saas_logs.csv (2.5 MB, 10,000 log entries)
Location: /home/ademm/saas-monitoring-platform/saas_logs.csv
```

## Troubleshooting

### "Invalid file type" Error
- Only .csv and .json files are accepted
- Check file extension (case-insensitive)

### "File size exceeds 100MB" Error
- File too large (max 100 MB)
- Compress or split the file

### "Network error occurred"
- Check Docker services are running: `docker ps`
- Verify Flask app is healthy: http://localhost:5000/api/health

### Table Not Loading
- Click "Refresh" button
- Check MongoDB is running
- Open browser console (F12) for errors

## API Testing (Advanced)

### Upload via cURL
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@saas_logs.csv"
```

### Get Recent Uploads
```bash
curl http://localhost:5000/api/uploads?limit=10
```

### Delete Upload
```bash
curl -X DELETE http://localhost:5000/api/uploads/{file_id}
```

## Next Steps

After uploading:
1. View logs in Dashboard: http://localhost:5000/
2. Search logs: http://localhost:5000/search
3. Analyze in Kibana: http://localhost:5601/

Enjoy your log monitoring platform! 🚀
