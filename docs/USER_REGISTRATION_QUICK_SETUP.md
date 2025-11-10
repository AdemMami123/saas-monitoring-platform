# User Registration - Quick Setup Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Rebuild the Application

The Docker container needs to install bcrypt:

```bash
cd saas-monitoring-platform
docker-compose up -d --build app
```

**Wait for build to complete** (about 1-2 minutes)

### Step 2: Verify Services

Check all services are running:

```bash
docker-compose ps
```

You should see:
- ✅ app (running)
- ✅ mongodb (running)
- ✅ redis (running)
- ✅ elasticsearch (running)

### Step 3: Check MongoDB Users Collection

Verify MongoDB is ready:

```bash
docker-compose exec mongodb mongosh -u admin -p password123 --eval "use saas_logs; db.users.countDocuments()"
```

Expected output: `0` (no users yet)

### Step 4: Access Registration Page

Open your browser:
```
http://localhost:5000/register
```

You should see a beautiful purple/blue gradient registration form.

### Step 5: Register Your First User

Fill in the form:
- **Username:** `admin` (3-20 chars, letters/numbers/underscores)
- **Email:** `admin@example.com`
- **Password:** `Admin123!` (8+ chars)
- **Confirm Password:** `Admin123!`

Click **"Create Account"**

### Step 6: Verify Registration

Check MongoDB:
```bash
docker-compose exec mongodb mongosh -u admin -p password123
```

Then in MongoDB shell:
```javascript
use saas_logs
db.users.find().pretty()
```

You should see your user with hashed password!

Check Redis session:
```bash
docker-compose exec redis redis-cli
KEYS session:*
GET session:{paste-session-id-here}
```

---

## 🧪 Test the API

### Test Registration API

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test1234",
    "confirm_password": "Test1234"
  }'
```

**Expected Success Response:**
```json
{
  "success": true,
  "redirect": "/",
  "message": "Welcome, testuser! Your account has been created successfully.",
  "user": {
    "id": "673...",
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

### Test Duplicate Username

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "another@example.com",
    "password": "Test1234",
    "confirm_password": "Test1234"
  }'
```

**Expected Error Response:**
```json
{
  "success": false,
  "error": "Username already exists",
  "field": "username"
}
```

### Test Invalid Email

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "invalid-email",
    "password": "Test1234",
    "confirm_password": "Test1234"
  }'
```

**Expected Error Response:**
```json
{
  "success": false,
  "error": "Invalid email format",
  "field": "email"
}
```

---

## 📁 Files Created/Modified

### ✅ New Files Created

1. **`app/models/__init__.py`**
   - Models package initialization
   - Exports User class

2. **`app/models/user.py`**
   - Complete User model (450+ lines)
   - MongoDB integration
   - bcrypt password hashing
   - Authentication methods
   - CRUD operations

3. **`app/templates/register.html`**
   - Bootstrap 5 registration form (600+ lines)
   - Client-side validation
   - Password strength indicator
   - AJAX submission
   - Beautiful gradient UI

4. **`docs/USER_REGISTRATION_IMPLEMENTATION.md`**
   - Complete implementation documentation
   - API reference
   - Troubleshooting guide

5. **`docs/USER_REGISTRATION_QUICK_SETUP.md`** (this file)
   - Quick setup instructions
   - Testing guide

### ✅ Modified Files

1. **`app/requirements.txt`**
   - Added: `bcrypt==4.1.0`

2. **`app/app.py`**
   - Added: `import re`
   - Added: `from flask import session`
   - Added: `from models.user import User`
   - Added: `app.config['SECRET_KEY']`
   - Added: `GET /register` route
   - Added: `POST /api/register` endpoint

---

## 🔧 Troubleshooting

### Problem: bcrypt module not found

**Symptoms:**
```
ModuleNotFoundError: No module named 'bcrypt'
```

**Solution:**
```bash
# Rebuild the app container
docker-compose up -d --build app

# Or install manually
docker-compose exec app pip install bcrypt==4.1.0
```

### Problem: MongoDB connection failed

**Symptoms:**
```
MongoDB connection error: ...
```

**Solution:**
```bash
# Check MongoDB is running
docker-compose ps mongodb

# Restart MongoDB
docker-compose restart mongodb

# Check logs
docker-compose logs mongodb
```

### Problem: Redis session error

**Symptoms:**
```
Redis session creation error: ...
```

**Solution:**
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping

# Should return: PONG
```

### Problem: Cannot import User model

**Symptoms:**
```
ImportError: cannot import name 'User' from 'models.user'
```

**Solution:**
```bash
# Make sure __init__.py exists
ls app/models/__init__.py

# Restart app container
docker-compose restart app
```

### Problem: Registration page not found (404)

**Symptoms:**
```
404 Not Found
```

**Solution:**
```bash
# Check app logs
docker-compose logs app

# Verify route is registered
docker-compose exec app python -c "from app import app; print(list(app.url_map.iter_rules()))"

# Restart app
docker-compose restart app
```

### Problem: User not created in MongoDB

**Symptoms:**
- API returns success but user not in database

**Solution:**
```bash
# Check MongoDB connection in app logs
docker-compose logs app | grep -i mongodb

# Test MongoDB directly
docker-compose exec mongodb mongosh -u admin -p password123 --eval "use saas_logs; db.users.find()"

# Check for errors in user.py
docker-compose exec app python -c "from models.user import User; print(User.create('test', 'test@test.com', 'Test1234'))"
```

---

## 🎯 What Works

✅ **Complete Registration Flow**
- Beautiful UI with gradient design
- Real-time client-side validation
- Password strength indicator
- Server-side validation
- Duplicate checking (username & email)
- bcrypt password hashing
- MongoDB user storage
- Redis session creation
- Success/error feedback
- Auto-redirect after registration

✅ **Security Features**
- Password hashing with bcrypt
- Unique username/email constraints
- Input validation (client + server)
- Session management
- XSS protection (Flask auto-escape)
- SQL injection prevention (MongoDB)

✅ **User Experience**
- Responsive design
- Smooth animations
- Password visibility toggle
- Loading states
- Helpful error messages
- Requirements checklist

---

## ❌ What's Missing

The following features are **NOT YET IMPLEMENTED**:

1. **Login System**
   - Login page
   - Login API endpoint
   - Session validation

2. **Logout**
   - Logout endpoint
   - Session cleanup

3. **Protected Routes**
   - Login required decorator
   - Middleware for auth check

4. **Password Reset**
   - Forgot password flow
   - Email integration

5. **User Profile**
   - Profile page
   - Edit profile
   - Avatar upload

See `USER_REGISTRATION_IMPLEMENTATION.md` for complete list of missing features.

---

## 📊 Validation Rules

### Username
- ✅ Required
- ✅ 3-20 characters
- ✅ Only letters, numbers, underscores
- ✅ Must be unique
- ❌ Case-sensitive

### Email
- ✅ Required
- ✅ Valid email format
- ✅ Must be unique
- ❌ Not verified (yet)

### Password
- ✅ Required
- ✅ Minimum 8 characters
- ✅ Hashed with bcrypt
- ❌ No maximum length enforced
- ❌ No complexity requirements (uppercase, special chars)

---

## 🔐 Security Checklist

- [x] Passwords are hashed (never stored plain text)
- [x] bcrypt with automatic salt generation
- [x] Unique constraints on username/email
- [x] Input validation (client + server)
- [x] XSS protection (Flask templates)
- [x] SQL injection prevention (MongoDB)
- [x] Session management (Redis)
- [ ] Rate limiting (TODO)
- [ ] CSRF protection (TODO)
- [ ] Email verification (TODO)
- [ ] 2FA (TODO)

---

## 🎓 Next Steps

To complete the authentication system:

### 1. Implement Login (30 minutes)

Create `login.html` and add login endpoint:

```python
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    user = User.authenticate(data['username'], data['password'])
    if user:
        session['user_id'] = user['_id']
        session['username'] = user['username']
        return jsonify({'success': True, 'redirect': '/'})
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
```

### 2. Add Logout (10 minutes)

```python
@app.route('/api/logout', methods=['POST'])
def logout_user():
    session.clear()
    return jsonify({'success': True, 'redirect': '/login'})
```

### 3. Protect Routes (20 minutes)

```python
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def dashboard():
    return render_template('index.html')
```

### 4. Test Everything (15 minutes)

- Register new user
- Login with credentials
- Access protected pages
- Logout
- Try accessing pages after logout

---

## 📞 Support

Need help?

1. **Check Logs:**
   ```bash
   docker-compose logs app
   docker-compose logs mongodb
   docker-compose logs redis
   ```

2. **Verify Database:**
   ```bash
   # MongoDB
   docker-compose exec mongodb mongosh -u admin -p password123
   use saas_logs
   db.users.find()
   
   # Redis
   docker-compose exec redis redis-cli
   KEYS *
   ```

3. **Test API:**
   ```bash
   curl -X POST http://localhost:5000/api/register \
     -H "Content-Type: application/json" \
     -d '{"username":"test","email":"test@test.com","password":"Test1234","confirm_password":"Test1234"}'
   ```

4. **Check Documentation:**
   - `USER_REGISTRATION_IMPLEMENTATION.md` - Complete guide
   - `QUICK_REFERENCE.md` - Project overview

---

**Status:** ✅ Registration system is fully functional!  
**Next:** Implement login system  
**Time to complete:** ~5 minutes setup + ~1 hour for login system

---

*Last updated: November 10, 2025*
