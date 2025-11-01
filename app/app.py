import os
import csv
import json
import subprocess
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from elasticsearch import Elasticsearch
from pymongo import MongoClient
import redis
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import uuid
import io

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration from environment variables
ES_HOST = os.getenv('ELASTICSEARCH_HOST', 'http://localhost:9200')
MONGO_HOST = os.getenv('MONGODB_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGODB_PORT', 27017))
MONGO_USER = os.getenv('MONGODB_USER', 'admin')
MONGO_PASSWORD = os.getenv('MONGODB_PASSWORD', 'password123')
MONGO_DATABASE = os.getenv('MONGODB_DATABASE', 'saas_logs')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# File upload configuration
UPLOAD_FOLDER = '/app/uploads'
ALLOWED_EXTENSIONS = {'csv', 'json'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB in bytes
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize clients
es_client = None
mongo_client = None
redis_client = None

def init_elasticsearch():
    """Initialize Elasticsearch client"""
    global es_client
    try:
        es_client = Elasticsearch(
            [ES_HOST],
            verify_certs=False,
            request_timeout=30
        )
        return es_client.ping()
    except Exception as e:
        print(f"Elasticsearch connection error: {e}")
        return False

def init_mongodb():
    """Initialize MongoDB client"""
    global mongo_client
    try:
        mongo_client = MongoClient(
            host=MONGO_HOST,
            port=MONGO_PORT,
            username=MONGO_USER,
            password=MONGO_PASSWORD,
            serverSelectionTimeoutMS=5000
        )
        # Test connection
        mongo_client.admin.command('ping')
        return True
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return False

def init_redis():
    """Initialize Redis client"""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=5
        )
        redis_client.ping()
        return True
    except Exception as e:
        print(f"Redis connection error: {e}")
        return False

# Initialize all connections
init_elasticsearch()
init_mongodb()
init_redis()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def dashboard():
    """Render main dashboard"""
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    """Render file upload page"""
    return render_template('upload.html')

@app.route('/search')
def search_page():
    """Render log search page"""
    return render_template('search.html')

@app.route('/api/health')
def health_check():
    """Check health of all services"""
    health_status = {
        'timestamp': datetime.utcnow().isoformat(),
        'services': {}
    }
    
    # Check Elasticsearch
    try:
        es_healthy = es_client and es_client.ping()
        health_status['services']['elasticsearch'] = {
            'status': 'healthy' if es_healthy else 'unhealthy',
            'host': ES_HOST
        }
        if es_healthy:
            cluster_health = es_client.cluster.health()
            health_status['services']['elasticsearch']['cluster_status'] = cluster_health.get('status', 'unknown')
    except Exception as e:
        health_status['services']['elasticsearch'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Check MongoDB
    try:
        mongo_client.admin.command('ping')
        health_status['services']['mongodb'] = {
            'status': 'healthy',
            'host': f"{MONGO_HOST}:{MONGO_PORT}"
        }
    except Exception as e:
        health_status['services']['mongodb'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Check Redis
    try:
        redis_client.ping()
        redis_info = redis_client.info('memory')
        health_status['services']['redis'] = {
            'status': 'healthy',
            'host': f"{REDIS_HOST}:{REDIS_PORT}",
            'memory_used': redis_info.get('used_memory_human', 'N/A')
        }
    except Exception as e:
        health_status['services']['redis'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Determine overall status
    all_healthy = all(
        service.get('status') == 'healthy' 
        for service in health_status['services'].values()
    )
    health_status['overall_status'] = 'healthy' if all_healthy else 'degraded'
    
    status_code = 200 if all_healthy else 503
    return jsonify(health_status), status_code

@app.route('/api/stats')
def get_stats():
    """Get log statistics from Elasticsearch"""
    stats = {
        'timestamp': datetime.utcnow().isoformat(),
        'total_logs': 0,
        'indices': [],
        'error': None
    }
    
    try:
        if not es_client:
            raise Exception("Elasticsearch client not initialized")
        
        # Get count of all documents in saas-logs-* indices
        count_result = es_client.count(index="saas-logs-*")
        stats['total_logs'] = count_result.get('count', 0)
        
        # Get index information
        indices = es_client.cat.indices(index="saas-logs-*", format="json")
        for index in indices:
            stats['indices'].append({
                'name': index.get('index'),
                'docs_count': index.get('docs.count', 0),
                'size': index.get('store.size', 'N/A')
            })
        
        # Cache result in Redis for 30 seconds
        if redis_client:
            redis_client.setex(
                'stats:total_logs',
                30,
                str(stats['total_logs'])
            )
    
    except Exception as e:
        stats['error'] = str(e)
        # Try to get cached value from Redis
        if redis_client:
            cached_count = redis_client.get('stats:total_logs')
            if cached_count:
                stats['total_logs'] = int(cached_count)
                stats['cached'] = True
    
    return jsonify(stats)

@app.route('/api/logs/recent')
def get_recent_logs():
    """Get recent logs from Elasticsearch"""
    try:
        if not es_client:
            return jsonify({'error': 'Elasticsearch not available'}), 503
        
        # Query for recent logs
        query = {
            "query": {"match_all": {}},
            "sort": [{"@timestamp": {"order": "desc"}}],
            "size": 50
        }
        
        result = es_client.search(index="saas-logs-*", body=query)
        
        logs = []
        for hit in result['hits']['hits']:
            log_entry = hit['_source']
            log_entry['_id'] = hit['_id']
            log_entry['_index'] = hit['_index']
            logs.append(log_entry)
        
        return jsonify({
            'total': result['hits']['total']['value'],
            'logs': logs
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs/stats/by-level')
def get_logs_by_level():
    """Get log count grouped by level"""
    try:
        if not es_client:
            return jsonify({'error': 'Elasticsearch not available'}), 503
        
        query = {
            "size": 0,
            "aggs": {
                "levels": {
                    "terms": {
                        "field": "level.keyword",
                        "size": 10
                    }
                }
            }
        }
        
        result = es_client.search(index="saas-logs-*", body=query)
        
        levels = []
        for bucket in result['aggregations']['levels']['buckets']:
            levels.append({
                'level': bucket['key'],
                'count': bucket['doc_count']
            })
        
        return jsonify({'levels': levels})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload CSV or JSON file, save to uploads folder and store metadata in MongoDB"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in request'}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Only CSV and JSON files are accepted'}), 400
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Secure the filename and add file_id prefix
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        new_filename = f"{file_id}.{file_extension}"
        
        # Save file to uploads folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Read first 10 lines for preview
        preview_lines = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i >= 10:
                        break
                    preview_lines.append(line.strip())
        except Exception as e:
            preview_lines = [f"Could not read preview: {str(e)}"]
        
        # Count records in file
        record_count = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_extension == 'csv':
                    record_count = sum(1 for line in f) - 1  # Subtract header
                elif file_extension == 'json':
                    data = json.load(f)
                    record_count = len(data) if isinstance(data, list) else 1
        except Exception as e:
            print(f"Could not count records: {e}")
        
        # Store metadata in MongoDB
        processing_status = 'uploaded'
        if mongo_client:
            db = mongo_client[MONGO_DATABASE]
            uploads_collection = db['uploads']
            
            metadata = {
                'file_id': file_id,
                'original_filename': original_filename,
                'stored_filename': new_filename,
                'file_type': file_extension,
                'file_size': file_size,
                'file_size_human': f"{file_size / 1024:.2f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.2f} MB",
                'upload_timestamp': datetime.utcnow(),
                'file_path': file_path,
                'preview': preview_lines[:10],
                'record_count': record_count,
                'processing_status': processing_status,
                'logstash_triggered': False
            }
            
            uploads_collection.insert_one(metadata)
        
        # Trigger Logstash processing by restarting the Logstash container
        # This forces Logstash to re-read the uploads directory
        logstash_triggered = False
        logstash_message = ""
        try:
            # Check if running in Docker environment
            result = subprocess.run(
                ['docker', 'restart', 'saas-logstash'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logstash_triggered = True
                logstash_message = "Logstash processing triggered successfully"
                processing_status = 'processing'
                
                # Update MongoDB with Logstash trigger status
                if mongo_client:
                    uploads_collection.update_one(
                        {'file_id': file_id},
                        {'$set': {
                            'logstash_triggered': True,
                            'logstash_triggered_at': datetime.utcnow(),
                            'processing_status': processing_status
                        }}
                    )
            else:
                logstash_message = f"Could not trigger Logstash: {result.stderr}"
                
        except FileNotFoundError:
            logstash_message = "Docker command not available. Logstash will process the file on its next scan cycle."
        except subprocess.TimeoutExpired:
            logstash_message = "Logstash restart timed out. File will be processed on next scan."
        except Exception as e:
            logstash_message = f"Error triggering Logstash: {str(e)}"
        
        # Cache upload info in Redis
        if redis_client:
            try:
                redis_client.setex(
                    f'upload:{file_id}',
                    3600,  # 1 hour TTL
                    json.dumps({
                        'file_id': file_id,
                        'filename': original_filename,
                        'status': processing_status,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                )
            except Exception as e:
                print(f"Redis cache error: {e}")
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': original_filename,
            'file_size': file_size,
            'file_size_human': metadata['file_size_human'],
            'record_count': record_count,
            'upload_timestamp': datetime.utcnow().isoformat(),
            'preview': preview_lines,
            'processing_status': processing_status,
            'logstash_triggered': logstash_triggered,
            'logstash_message': logstash_message
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/uploads', methods=['GET'])
def get_uploads():
    """Get list of uploaded files from MongoDB"""
    try:
        if not mongo_client:
            return jsonify({'error': 'MongoDB not available'}), 503
        
        db = mongo_client[MONGO_DATABASE]
        uploads_collection = db['uploads']
        
        # Get all uploads, sorted by upload timestamp (newest first)
        uploads = list(uploads_collection.find(
            {},
            {'_id': 0}
        ).sort('upload_timestamp', -1).limit(100))
        
        # Convert datetime to ISO format
        for upload in uploads:
            if 'upload_timestamp' in upload:
                upload['upload_timestamp'] = upload['upload_timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'count': len(uploads),
            'uploads': uploads
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs/search', methods=['GET'])
def search_logs():
    """Search logs with filters and pagination"""
    try:
        if not es_client:
            return jsonify({'error': 'Elasticsearch not available'}), 503
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        log_level = request.args.get('level', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        endpoint = request.args.get('endpoint', '')
        search_text = request.args.get('q', '')
        
        # Build Elasticsearch query
        must_conditions = []
        
        # Add log level filter
        if log_level:
            must_conditions.append({
                "term": {"level.keyword": log_level}
            })
        
        # Add endpoint filter
        if endpoint:
            must_conditions.append({
                "match": {"endpoint": endpoint}
            })
        
        # Add date range filter
        if start_date or end_date:
            date_range = {}
            if start_date:
                date_range["gte"] = start_date
            if end_date:
                date_range["lte"] = end_date
            
            must_conditions.append({
                "range": {"@timestamp": date_range}
            })
        
        # Add text search
        if search_text:
            must_conditions.append({
                "multi_match": {
                    "query": search_text,
                    "fields": ["message", "endpoint", "user_id"]
                }
            })
        
        # Build final query
        query = {
            "query": {
                "bool": {
                    "must": must_conditions if must_conditions else [{"match_all": {}}]
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}],
            "from": (page - 1) * per_page,
            "size": per_page
        }
        
        result = es_client.search(index="saas-logs-*", body=query)
        
        logs = []
        for hit in result['hits']['hits']:
            log_entry = hit['_source']
            log_entry['_id'] = hit['_id']
            log_entry['_index'] = hit['_index']
            logs.append(log_entry)
        
        total = result['hits']['total']['value']
        total_pages = (total + per_page - 1) // per_page
        
        return jsonify({
            'success': True,
            'logs': logs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs/export', methods=['POST'])
def export_logs():
    """Export filtered logs to CSV"""
    try:
        if not es_client:
            return jsonify({'error': 'Elasticsearch not available'}), 503
        
        # Get filter parameters from request body
        data = request.get_json() or {}
        log_level = data.get('level', '')
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        endpoint = data.get('endpoint', '')
        search_text = data.get('q', '')
        
        # Build query (same as search)
        must_conditions = []
        
        if log_level:
            must_conditions.append({"term": {"level.keyword": log_level}})
        if endpoint:
            must_conditions.append({"match": {"endpoint": endpoint}})
        if start_date or end_date:
            date_range = {}
            if start_date:
                date_range["gte"] = start_date
            if end_date:
                date_range["lte"] = end_date
            must_conditions.append({"range": {"@timestamp": date_range}})
        if search_text:
            must_conditions.append({
                "multi_match": {
                    "query": search_text,
                    "fields": ["message", "endpoint", "user_id"]
                }
            })
        
        query = {
            "query": {
                "bool": {
                    "must": must_conditions if must_conditions else [{"match_all": {}}]
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}],
            "size": 10000  # Max export limit
        }
        
        result = es_client.search(index="saas-logs-*", body=query)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Timestamp', 'Level', 'Endpoint', 'User ID', 'Message', 'Response Time'])
        
        # Write data
        for hit in result['hits']['hits']:
            log = hit['_source']
            writer.writerow([
                log.get('@timestamp', ''),
                log.get('level', ''),
                log.get('endpoint', ''),
                log.get('user_id', ''),
                log.get('message', ''),
                log.get('response_time', '')
            ])
        
        # Prepare file for download
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'logs_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
