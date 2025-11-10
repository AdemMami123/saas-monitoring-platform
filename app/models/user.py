"""
User model for authentication and user management
"""
import os
import bcrypt
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId


class User:
    """User model with MongoDB integration"""
    
    # MongoDB connection settings from environment
    MONGO_HOST = os.getenv('MONGODB_HOST', 'localhost')
    MONGO_PORT = int(os.getenv('MONGODB_PORT', 27017))
    MONGO_USER = os.getenv('MONGODB_USER', 'admin')
    MONGO_PASSWORD = os.getenv('MONGODB_PASSWORD', 'password123')
    MONGO_DATABASE = os.getenv('MONGODB_DATABASE', 'saas_logs')
    
    _client = None
    _db = None
    _collection = None
    
    @classmethod
    def _get_collection(cls):
        """Get or create MongoDB collection connection"""
        if cls._collection is None:
            try:
                cls._client = MongoClient(
                    host=cls.MONGO_HOST,
                    port=cls.MONGO_PORT,
                    username=cls.MONGO_USER,
                    password=cls.MONGO_PASSWORD,
                    serverSelectionTimeoutMS=5000
                )
                cls._db = cls._client[cls.MONGO_DATABASE]
                cls._collection = cls._db['users']
                
                # Create unique indexes for username and email
                cls._collection.create_index('username', unique=True)
                cls._collection.create_index('email', unique=True)
                
            except Exception as e:
                print(f"MongoDB connection error: {e}")
                raise
        
        return cls._collection
    
    @classmethod
    def create(cls, username, email, password):
        """
        Create a new user with hashed password
        
        Args:
            username (str): Unique username (3-20 characters)
            email (str): Unique email address
            password (str): Plain text password (will be hashed)
        
        Returns:
            str: User ID on success
            None: On failure
        
        Raises:
            ValueError: If username or email already exists
            Exception: For other database errors
        """
        try:
            collection = cls._get_collection()
            
            # Check for duplicate username
            if collection.find_one({'username': username}):
                raise ValueError('Username already exists')
            
            # Check for duplicate email
            if collection.find_one({'email': email}):
                raise ValueError('Email already exists')
            
            # Hash the password with bcrypt
            password_hash = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            )
            
            # Create user document
            user_doc = {
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_active': True,
                'last_login': None,
                'profile': {
                    'display_name': username,
                    'avatar_url': None
                }
            }
            
            # Insert into MongoDB
            result = collection.insert_one(user_doc)
            
            return str(result.inserted_id)
            
        except ValueError as e:
            # Re-raise ValueError for duplicate checks
            raise
        except Exception as e:
            print(f"Error creating user: {e}")
            raise Exception(f"Failed to create user: {str(e)}")
    
    @classmethod
    def authenticate(cls, username, password):
        """
        Authenticate user with username and password
        
        Args:
            username (str): Username or email
            password (str): Plain text password
        
        Returns:
            dict: User document (without password_hash) on success
            None: On authentication failure
        """
        try:
            collection = cls._get_collection()
            
            # Find user by username or email
            user = collection.find_one({
                '$or': [
                    {'username': username},
                    {'email': username}
                ]
            })
            
            if not user:
                return None
            
            # Check if user is active
            if not user.get('is_active', True):
                return None
            
            # Verify password
            if bcrypt.checkpw(
                password.encode('utf-8'),
                user['password_hash']
            ):
                # Update last login time
                collection.update_one(
                    {'_id': user['_id']},
                    {'$set': {'last_login': datetime.utcnow()}}
                )
                
                # Remove password hash from returned document
                user.pop('password_hash', None)
                user['_id'] = str(user['_id'])
                
                return user
            
            return None
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    @classmethod
    def get_by_username(cls, username):
        """
        Get user by username
        
        Args:
            username (str): Username to search for
        
        Returns:
            dict: User document (without password_hash) or None
        """
        try:
            collection = cls._get_collection()
            
            user = collection.find_one({'username': username})
            
            if user:
                user.pop('password_hash', None)
                user['_id'] = str(user['_id'])
                return user
            
            return None
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    @classmethod
    def get_by_id(cls, user_id):
        """
        Get user by ID
        
        Args:
            user_id (str): User ID (MongoDB ObjectId as string)
        
        Returns:
            dict: User document (without password_hash) or None
        """
        try:
            collection = cls._get_collection()
            
            user = collection.find_one({'_id': ObjectId(user_id)})
            
            if user:
                user.pop('password_hash', None)
                user['_id'] = str(user['_id'])
                return user
            
            return None
            
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    @classmethod
    def get_by_email(cls, email):
        """
        Get user by email
        
        Args:
            email (str): Email address to search for
        
        Returns:
            dict: User document (without password_hash) or None
        """
        try:
            collection = cls._get_collection()
            
            user = collection.find_one({'email': email})
            
            if user:
                user.pop('password_hash', None)
                user['_id'] = str(user['_id'])
                return user
            
            return None
            
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    @classmethod
    def update(cls, user_id, update_data):
        """
        Update user information
        
        Args:
            user_id (str): User ID
            update_data (dict): Fields to update
        
        Returns:
            bool: True on success, False on failure
        """
        try:
            collection = cls._get_collection()
            
            # Don't allow updating sensitive fields directly
            forbidden_fields = ['password_hash', '_id', 'created_at']
            for field in forbidden_fields:
                update_data.pop(field, None)
            
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            result = collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    @classmethod
    def change_password(cls, user_id, old_password, new_password):
        """
        Change user password
        
        Args:
            user_id (str): User ID
            old_password (str): Current password (for verification)
            new_password (str): New password
        
        Returns:
            bool: True on success, False on failure
        """
        try:
            collection = cls._get_collection()
            
            # Get user with password hash
            user = collection.find_one({'_id': ObjectId(user_id)})
            
            if not user:
                return False
            
            # Verify old password
            if not bcrypt.checkpw(
                old_password.encode('utf-8'),
                user['password_hash']
            ):
                return False
            
            # Hash new password
            new_password_hash = bcrypt.hashpw(
                new_password.encode('utf-8'),
                bcrypt.gensalt()
            )
            
            # Update password
            result = collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'password_hash': new_password_hash,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error changing password: {e}")
            return False
    
    @classmethod
    def delete(cls, user_id):
        """
        Delete user (soft delete by setting is_active to False)
        
        Args:
            user_id (str): User ID
        
        Returns:
            bool: True on success, False on failure
        """
        try:
            collection = cls._get_collection()
            
            result = collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'is_active': False,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
