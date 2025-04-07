from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)
uri = 'mongodb://root:abc123...@localhost:27017/'
client = MongoClient(uri)

db = client.get_database("Django_Music")
print(db.list_collection_names())


@app.route('/testing', methods=('GET', 'POST'))
def index():
    return render_template('test2.html')

@app.route('/home', methods=('GET', 'POST'))
def landingpage():
    return render_template('landingpage.html')
@app.route('/search', methods=('GET', 'POST'))
def searchpage():
    return render_template('searchpage.html')
@app.route('/add_document', methods=['POST'])
def add_document():
    try:
        data = request.json  # Get JSON data from request
        if not data:
            return jsonify({"error": "No data provided"}), 400

        result = db.mycollection.insert_one(data)  # Insert into MongoDB
        return jsonify({"message": "Document added", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500