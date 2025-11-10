import os
import csv
import json
import subprocess
import time
from datetime import datetime, timedelta
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
    """Get comprehensive dashboard statistics"""
    stats = {
        'timestamp': datetime.utcnow().isoformat(),
        'total_logs': 0,
        'total_logs_24h': 0,
        'error_rate': 0,
        'avg_response_time': 0,
        'top_slowest_endpoints': [],
        'active_users': 0,
        'latest_error': None,
        'files_uploaded': 0,
        'system_status': {
            'elasticsearch': 'unknown',
            'mongodb': 'unknown',
            'redis': 'unknown',
            'overall': 'degraded'
        },
        'indices': [],
        'hourly_trends': {
            'logs': [],
            'errors': [],
            'response_times': []
        },
        'error': None
    }
    
    try:
        if not es_client:
            raise Exception("Elasticsearch client not initialized")
        
        # Calculate 24h timestamp
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_24h_str = last_24h.isoformat()
        
        # 1. Total logs (all time)
        count_result = es_client.count(index="saas-logs-*")
        stats['total_logs'] = count_result.get('count', 0)
        
        # 2. Total logs (last 24 hours)
        count_24h_query = {
            "query": {
                "range": {
                    "timestamp": {
                        "gte": last_24h_str
                    }
                }
            }
        }
        count_24h_result = es_client.count(index="saas-logs-*", body=count_24h_query)
        stats['total_logs_24h'] = count_24h_result.get('count', 0)
        
        # 3. Error rate: (5xx errors / total requests) * 100
        error_query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": last_24h_str}}},
                        {"range": {"status_code": {"gte": 500, "lt": 600}}}
                    ]
                }
            }
        }
        error_count = es_client.count(index="saas-logs-*", body=error_query).get('count', 0)
        if stats['total_logs_24h'] > 0:
            stats['error_rate'] = round((error_count / stats['total_logs_24h']) * 100, 2)
        
        # 4. Average response time (last 24h)
        avg_response_query = {
            "query": {
                "range": {
                    "timestamp": {
                        "gte": last_24h_str
                    }
                }
            },
            "aggs": {
                "avg_response": {
                    "avg": {
                        "field": "response_time_ms"
                    }
                }
            },
            "size": 0
        }
        avg_response_result = es_client.search(index="saas-logs-*", body=avg_response_query)
        avg_value = avg_response_result.get('aggregations', {}).get('avg_response', {}).get('value')
        stats['avg_response_time'] = round(avg_value, 0) if avg_value else 0
        
        # 5. Top 3 slowest endpoints
        slowest_endpoints_query = {
            "query": {
                "range": {
                    "timestamp": {
                        "gte": last_24h_str
                    }
                }
            },
            "aggs": {
                "endpoints": {
                    "terms": {
                        "field": "endpoint.keyword",
                        "size": 3,
                        "order": {
                            "avg_response": "desc"
                        }
                    },
                    "aggs": {
                        "avg_response": {
                            "avg": {
                                "field": "response_time_ms"
                            }
                        }
                    }
                }
            },
            "size": 0
        }
        slowest_result = es_client.search(index="saas-logs-*", body=slowest_endpoints_query)
        for bucket in slowest_result.get('aggregations', {}).get('endpoints', {}).get('buckets', []):
            stats['top_slowest_endpoints'].append({
                'endpoint': bucket.get('key'),
                'avg_response_time': round(bucket.get('avg_response', {}).get('value', 0), 0),
                'count': bucket.get('doc_count', 0)
            })
        
        # 6. Active users (unique user_ids, last 24h)
        active_users_query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": last_24h_str}}},
                        {"exists": {"field": "user_id"}}
                    ]
                }
            },
            "aggs": {
                "unique_users": {
                    "cardinality": {
                        "field": "user_id.keyword"
                    }
                }
            },
            "size": 0
        }
        active_users_result = es_client.search(index="saas-logs-*", body=active_users_query)
        stats['active_users'] = active_users_result.get('aggregations', {}).get('unique_users', {}).get('value', 0)
        
        # 7. Latest error (most recent ERROR or CRITICAL log)
        latest_error_query = {
            "query": {
                "bool": {
                    "should": [
                        {"term": {"level.keyword": "ERROR"}},
                        {"term": {"level.keyword": "CRITICAL"}}
                    ],
                    "minimum_should_match": 1
                }
            },
            "sort": [{"timestamp": {"order": "desc"}}],
            "size": 1
        }
        latest_error_result = es_client.search(index="saas-logs-*", body=latest_error_query)
        if latest_error_result['hits']['hits']:
            error_log = latest_error_result['hits']['hits'][0]['_source']
            stats['latest_error'] = {
                'timestamp': error_log.get('timestamp'),
                'level': error_log.get('level'),
                'message': error_log.get('message'),
                'endpoint': error_log.get('endpoint'),
                'status_code': error_log.get('status_code')
            }
        
        # 8. Files uploaded count (from MongoDB)
        if mongo_client:
            try:
                db = mongo_client[MONGO_DATABASE]
                files_collection = db['files']
                stats['files_uploaded'] = files_collection.count_documents({})
            except Exception as e:
                print(f"MongoDB files count error: {e}")
        
        # Get hourly trends for last 24 hours (for sparkline charts)
        hourly_trends_query = {
            "query": {
                "range": {
                    "timestamp": {
                        "gte": last_24h_str
                    }
                }
            },
            "aggs": {
                "hourly": {
                    "date_histogram": {
                        "field": "timestamp",
                        "fixed_interval": "1h",
                        "min_doc_count": 0,
                        "extended_bounds": {
                            "min": last_24h_str,
                            "max": now.isoformat()
                        }
                    },
                    "aggs": {
                        "error_count": {
                            "filter": {
                                "range": {
                                    "status_code": {
                                        "gte": 500,
                                        "lt": 600
                                    }
                                }
                            }
                        },
                        "avg_response": {
                            "avg": {
                                "field": "response_time_ms"
                            }
                        }
                    }
                }
            },
            "size": 0
        }
        trends_result = es_client.search(index="saas-logs-*", body=hourly_trends_query)
        for bucket in trends_result.get('aggregations', {}).get('hourly', {}).get('buckets', []):
            stats['hourly_trends']['logs'].append(bucket.get('doc_count', 0))
            stats['hourly_trends']['errors'].append(bucket.get('error_count', {}).get('doc_count', 0))
            avg_resp = bucket.get('avg_response', {}).get('value')
            stats['hourly_trends']['response_times'].append(round(avg_resp, 0) if avg_resp else 0)
        
        # 9. System status
        stats['system_status']['elasticsearch'] = 'healthy'
        
        # Check MongoDB
        if mongo_client:
            try:
                mongo_client.admin.command('ping')
                stats['system_status']['mongodb'] = 'healthy'
            except:
                stats['system_status']['mongodb'] = 'unhealthy'
        else:
            stats['system_status']['mongodb'] = 'unhealthy'
        
        # Check Redis
        if redis_client:
            try:
                redis_client.ping()
                stats['system_status']['redis'] = 'healthy'
            except:
                stats['system_status']['redis'] = 'unhealthy'
        else:
            stats['system_status']['redis'] = 'unhealthy'
        
        # Overall status
        all_healthy = all(
            status == 'healthy' 
            for status in [
                stats['system_status']['elasticsearch'],
                stats['system_status']['mongodb'],
                stats['system_status']['redis']
            ]
        )
        stats['system_status']['overall'] = 'healthy' if all_healthy else 'degraded'
        
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
            try:
                redis_client.setex(
                    'stats:dashboard',
                    30,
                    json.dumps(stats)
                )
            except Exception as e:
                print(f"Redis cache error: {e}")
    
    except Exception as e:
        stats['error'] = str(e)
        # Try to get cached value from Redis
        if redis_client:
            try:
                cached_stats = redis_client.get('stats:dashboard')
                if cached_stats:
                    cached_data = json.loads(cached_stats)
                    cached_data['cached'] = True
                    cached_data['cache_error'] = str(e)
                    return jsonify(cached_data)
            except:
                pass
    
    return jsonify(stats)

@app.route('/api/search', methods=['POST'])
def comprehensive_search():
    """Comprehensive search endpoint with filters and pagination"""
    try:
        if not es_client:
            return jsonify({'error': 'Elasticsearch not available'}), 503
        
        # Get parameters from request
        data = request.get_json() or {}
        search_query = data.get('q', '').strip()
        log_level = data.get('level', '')
        date_from = data.get('date_from', '')
        date_to = data.get('date_to', '')
        endpoint_filter = data.get('endpoint', '')
        status_code = data.get('status_code', '')
        server = data.get('server', '')
        page = int(data.get('page', 1))
        per_page = int(data.get('per_page', 50))
        sort_field = data.get('sort_field', 'timestamp')
        sort_order = data.get('sort_order', 'desc')
        
        # Build Elasticsearch query
        must_conditions = []
        filter_conditions = []
        
        # Search query in message field
        if search_query:
            must_conditions.append({
                "multi_match": {
                    "query": search_query,
                    "fields": ["message", "endpoint", "user_agent"],
                    "type": "best_fields",
                    "operator": "or"
                }
            })
        
        # Log level filter
        if log_level and log_level != 'ALL':
            filter_conditions.append({
                "term": {"level.keyword": log_level}
            })
        
        # Date range filter
        if date_from or date_to:
            date_range = {}
            if date_from:
                date_range["gte"] = date_from
            if date_to:
                date_range["lte"] = date_to
            filter_conditions.append({
                "range": {"timestamp": date_range}
            })
        
        # Endpoint filter
        if endpoint_filter:
            filter_conditions.append({
                "term": {"endpoint.keyword": endpoint_filter}
            })
        
        # Status code filter
        if status_code:
            if status_code == '2xx':
                filter_conditions.append({"range": {"status_code": {"gte": 200, "lt": 300}}})
            elif status_code == '4xx':
                filter_conditions.append({"range": {"status_code": {"gte": 400, "lt": 500}}})
            elif status_code == '5xx':
                filter_conditions.append({"range": {"status_code": {"gte": 500, "lt": 600}}})
            else:
                filter_conditions.append({"term": {"status_code": int(status_code)}})
        
        # Server filter
        if server:
            filter_conditions.append({
                "term": {"server.keyword": server}
            })
        
        # Build query
        if must_conditions or filter_conditions:
            query = {
                "query": {
                    "bool": {
                        "must": must_conditions if must_conditions else [{"match_all": {}}],
                        "filter": filter_conditions
                    }
                }
            }
        else:
            query = {
                "query": {"match_all": {}}
            }
        
        # Add sorting
        sort_mapping = {
            'timestamp': 'timestamp',
            'level': 'level.keyword',
            'endpoint': 'endpoint.keyword',
            'status_code': 'status_code',
            'response_time_ms': 'response_time_ms'
        }
        sort_es_field = sort_mapping.get(sort_field, 'timestamp')
        query["sort"] = [{sort_es_field: {"order": sort_order}}]
        
        # Add pagination
        query["from"] = (page - 1) * per_page
        query["size"] = per_page
        
        # Execute search
        result = es_client.search(index="saas-logs-*", body=query)
        
        # Process results
        results = []
        for hit in result['hits']['hits']:
            log_entry = hit['_source']
            log_entry['_id'] = hit['_id']
            results.append(log_entry)
        
        total = result['hits']['total']['value']
        total_pages = (total + per_page - 1) // per_page
        
        return jsonify({
            'success': True,
            'results': results,
            'total': total,
            'page': page,
            'pages': total_pages,
            'per_page': per_page
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/search/endpoints', methods=['GET'])
def get_unique_endpoints():
    """Get unique endpoints for filter dropdown"""
    try:
        if not es_client:
            return jsonify({'error': 'Elasticsearch not available'}), 503
        
        query = {
            "size": 0,
            "aggs": {
                "unique_endpoints": {
                    "terms": {
                        "field": "endpoint.keyword",
                        "size": 100
                    }
                }
            }
        }
        
        result = es_client.search(index="saas-logs-*", body=query)
        
        endpoints = []
        for bucket in result['aggregations']['unique_endpoints']['buckets']:
            endpoints.append(bucket['key'])
        
        return jsonify({
            'success': True,
            'endpoints': endpoints
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
            return jsonify({'success': False, 'error': 'No file part in request'}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed. Only CSV and JSON files are accepted'}), 400
        
        # Generate unique filename with timestamp
        timestamp = int(time.time())
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        saved_filename = f"{timestamp}_{original_filename}"
        
        # Save file to uploads folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Count records in file (log_count)
        log_count = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_extension == 'csv':
                    log_count = sum(1 for line in f) - 1  # Subtract header
                elif file_extension == 'json':
                    data = json.load(f)
                    log_count = len(data) if isinstance(data, list) else 1
        except Exception as e:
            print(f"Could not count records: {e}")
        
        # Generate file ID
        file_id = str(uuid.uuid4())
        
        # Store metadata in MongoDB "files" collection as per requirements
        if mongo_client:
            db = mongo_client[MONGO_DATABASE]
            files_collection = db['files']
            
            metadata = {
                '_id': file_id,
                'filename': original_filename,
                'saved_as': saved_filename,
                'file_type': file_extension,
                'file_size': file_size,
                'upload_date': datetime.utcnow().isoformat() + 'Z',
                'log_count': log_count,
                'status': 'completed',
                'user': 'admin',
                'file_path': file_path
            }
            
            files_collection.insert_one(metadata)
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'message': 'File uploaded successfully',
            'filename': original_filename,
            'saved_as': saved_filename,
            'file_size': file_size,
            'log_count': log_count
        }), 201
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/uploads', methods=['GET'])
def get_uploads():
    """Get list of uploaded files from MongoDB"""
    try:
        if not mongo_client:
            return jsonify({'error': 'MongoDB not available'}), 503
        
        db = mongo_client[MONGO_DATABASE]
        files_collection = db['files']
        
        # Get last 10 uploads, sorted by upload date (newest first)
        limit = int(request.args.get('limit', 10))
        uploads = list(files_collection.find(
            {},
            {'file_path': 0}  # Exclude internal file path
        ).sort('upload_date', -1).limit(limit))
        
        # Convert _id to string for JSON serialization
        for upload in uploads:
            if '_id' in upload:
                upload['_id'] = str(upload['_id'])
        
        return jsonify({
            'success': True,
            'count': len(uploads),
            'uploads': uploads
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/uploads/<file_id>', methods=['DELETE'])
def delete_upload(file_id):
    """Delete an uploaded file"""
    try:
        if not mongo_client:
            return jsonify({'success': False, 'error': 'MongoDB not available'}), 503
        
        db = mongo_client[MONGO_DATABASE]
        files_collection = db['files']
        
        # Find the file metadata
        file_doc = files_collection.find_one({'_id': file_id})
        
        if not file_doc:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Delete physical file
        file_path = file_doc.get('file_path')
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete metadata from MongoDB
        files_collection.delete_one({'_id': file_id})
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
