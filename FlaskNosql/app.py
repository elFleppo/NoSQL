from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
CORS(app)
uri = 'mongodb://root:abc123...@localhost:27017/'
client = MongoClient(uri)

db = client.get_database("Django_Music")
print(db.list_collection_names())

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
        entities = list(collection.find({}, {'_id': 1, 'name': 1, 'firstname': 1, 'lastname': 1, 'orchestra_name': 1, 'piece_name': 1}))
        
        # Convert ObjectId to string for JSON serialization
        for entity in entities:
            entity['_id'] = str(entity['_id'])
        
        return jsonify(entities)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/testing', methods=('GET', 'POST'))
def index():
    return render_template('test2.html')

@app.route('/home', methods=('GET', 'POST'))
def landingpage():
    return render_template('landingpage.html')

@app.route('/searchpage', methods=['GET'])
def searchpage():
    return render_template('searchpage.html')

@app.route('/search', methods=['GET'])
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

@app.route('/add_document', methods=['POST'])
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

        result = db[collection_name].insert_one(data)
        return jsonify({"message": "Document added", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500