from flask import Flask, render_template, request, url_for, redirect, jsonify, flash, session
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from config import config
from models import User
from functools import wraps
from flask_session import Session
import shutil
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load configuration
app.config.from_object(config['development'])

# Initialize session
Session(app)

# Clean up old session files on startup
session_dir = app.config['SESSION_FILE_DIR']
if os.path.exists(session_dir):
    shutil.rmtree(session_dir)
os.makedirs(session_dir, exist_ok=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Add session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP in development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Construct MongoDB URI with authentication
def get_mongo_uri():
    if app.config['MONGO_USER'] and app.config['MONGO_PASSWORD']:
        return f'mongodb://{app.config["MONGO_USER"]}:{app.config["MONGO_PASSWORD"]}@{app.config["MONGO_HOST"]}:{app.config["MONGO_PORT"]}/{app.config["MONGO_DB"]}?authSource=admin'
    return f'mongodb://{app.config["MONGO_HOST"]}:{app.config["MONGO_PORT"]}/{app.config["MONGO_DB"]}'

# Initialize MongoDB connection
def init_mongodb():
    try:
        uri = get_mongo_uri()
        client = MongoClient(uri)
        
        # Test the connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

# Initialize MongoDB client
client = init_mongodb()
db = client[app.config["MONGO_DB"]]

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.is_admin = user_data.get('is_admin', False)
        self._authenticated = True

    @property
    def is_authenticated(self):
        return self._authenticated

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None
    except Exception as e:
        print(f"Error loading user: {e}")
        return None

# Routes for authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('landingpage'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_data = db.users.find_one({'username': username})
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user, remember=True)
            session.permanent = True
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('landingpage'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # If user is already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('landingpage'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = 'is_admin' in request.form
        
        # Only allow admin users to create other admin users
        if is_admin and (not current_user.is_authenticated or not current_user.is_admin):
            flash('Only administrators can create admin users', 'danger')
            return redirect(url_for('register'))
        
        # Check if username already exists
        if db.users.find_one({'username': username}):
            flash('Username already exists', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            user_data = {
                'username': username,
                'password': hashed_password,
                'is_admin': is_admin
            }
            db.users.insert_one(user_data)
            flash('User registered successfully. Please log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    # Clear the session cookie
    response = redirect(url_for('login'))
    response.delete_cookie('session')
    response.delete_cookie('remember_token')
    flash('You have been logged out', 'info')
    return response

# Create admin user if not exists
def create_admin_user():
    try:
        admin_username = app.config['ADMIN_USERNAME']
        admin_password = app.config['ADMIN_PASSWORD']
        
        if not db.users.find_one({'username': admin_username}):
            hashed_password = generate_password_hash(admin_password)
            admin_user = {
                'username': admin_username,
                'password': hashed_password,
                'is_admin': True
            }
            db.users.insert_one(admin_user)
            print(f"Admin user '{admin_username}' created")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        raise

# Call this function when the application starts
create_admin_user()

# Map entity types to their collections
entity_collections = {
    'Composer': 'composers',
    'Piece': 'pieces',
    'Orchestra': 'orchestras',
    'Conductor': 'conductors',
    'Review': 'reviews'
}

# Map entity types to their searchable fields
entity_search_fields = {
    'Composer': ['name', 'nationality'],
    'Piece': ['piece_name', 'era'],
    'Orchestra': ['orchestra_name'],
    'Conductor': ['firstname', 'lastname'],
    'Review': ['text_content']
}

@app.route('/get_entities/<entity_type>', methods=['GET'])
def get_entities(entity_type):
    try:
        collection_name = entity_collections.get(entity_type)
        if not collection_name:
            return jsonify({"error": "Invalid entity type"}), 400

        collection = db[collection_name]
        if collection is not db.users:
            entities = list(collection.find({}, {'_id': 1, 'name': 1, 'firstname': 1, 'lastname': 1, 'orchestra_name': 1, 'piece_name': 1}))
        else:
            entities = []
        
        # Convert ObjectId to string for JSON serialization
        for entity in entities:
            entity['_id'] = str(entity['_id'])
        
        return jsonify(entities)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add_document', methods=('GET', 'POST'))
def add_document_page():
    return render_template('add_document.html')

@app.route('/home', methods=('GET', 'POST'))
def landingpage():
    return render_template('landingpage.html')

@app.route('/searchpage')
@login_required
def searchpage():
    return render_template('searchpage.html')

@app.route('/search', methods=['GET'])
@login_required
def search():
    try:
        entity_type = request.args.get('entity_type', 'all')
        query = request.args.get('q', '')
        sort_by = request.args.get('sort', 'relevance')

        results = {}
        
        if entity_type == 'all':
            # Search across all collections
            for entity, collection_name in entity_collections.items():
                collection = db[collection_name]
                search_query = {}
                
                # Build search query based on entity's searchable fields
                if query:
                    search_query['$or'] = [
                        {field: {'$regex': query, '$options': 'i'}}
                        for field in entity_search_fields[entity]
                    ]
                
                # Execute search
                items = list(collection.find(search_query))
                
                # Convert ObjectId to string for JSON serialization
                for item in items:
                    item['_id'] = str(item['_id'])
                
                results[entity] = items
        else:
            # Search specific collection
            collection_name = entity_collections.get(entity_type)
            if not collection_name:
                return jsonify({"error": "Invalid entity type"}), 400

            collection = db[collection_name]
            search_query = {}
            
            # Build search query based on entity's searchable fields
            if query:
                search_query['$or'] = [
                    {field: {'$regex': query, '$options': 'i'}}
                    for field in entity_search_fields[entity_type]
                ]
            
            # Execute search
            items = list(collection.find(search_query))
            
            # Convert ObjectId to string for JSON serialization
            for item in items:
                item['_id'] = str(item['_id'])
            
            results[entity_type] = items

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Custom decorator for admin-only routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('landingpage'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/add_document', methods=['POST'])
@login_required
def add_document():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Determine the collection based on the entity type
        entity_type = request.args.get('entity_type')
        if not entity_type:
            return jsonify({"error": "Entity type not specified"}), 400

        collection_name = entity_collections.get(entity_type)
        if not collection_name:
            return jsonify({"error": "Invalid entity type"}), 400

        # Only allow admins to add data for non-review entities
        if entity_type != 'Review' and not current_user.is_admin:
            return jsonify({"error": "Only administrators can add this type of data"}), 403

        result = db[collection_name].insert_one(data)
        return jsonify({"message": "Document added", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check_admin')
@login_required
def check_admin():
    return jsonify({'is_admin': current_user.is_admin})

@app.route('/edit_document/<entity_type>/<document_id>', methods=['GET', 'POST'])
@login_required
def edit_document(entity_type, document_id):
    if not current_user.is_admin:
        flash('Only administrators can edit documents', 'danger')
        return redirect(url_for('searchpage'))

    collection_name = entity_collections.get(entity_type)
    if not collection_name:
        flash('Invalid entity type', 'danger')
        return redirect(url_for('searchpage'))

    if request.method == 'GET':
        document = db[collection_name].find_one({'_id': ObjectId(document_id)})
        if not document:
            flash('Document not found', 'danger')
            return redirect(url_for('searchpage'))
        
        return render_template('edit_form.html', 
                            document=document,
                            entity_type=entity_type,
                            document_id=document_id)
    
    elif request.method == 'POST':
        try:
            data = request.json
            if not data:
                return jsonify({"error": "No data provided"}), 400

            result = db[collection_name].update_one(
                {'_id': ObjectId(document_id)},
                {'$set': data}
            )

            if result.modified_count > 0:
                return jsonify({"message": "Document updated successfully"}), 200
            else:
                return jsonify({"error": "No changes made"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/check_login')
def check_login():
    return jsonify({'logged_in': current_user.is_authenticated if current_user.is_authenticated else False})