from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient

app = Flask(__name__)
uri = 'mongodb://root:abc123...@localhost:27017/'
client = MongoClient(uri)

db = client.get_database("Django_Music")
print(db.list_collection_names())


@app.route('/music', methods=('GET', 'POST'))
def index():
    return render_template('index.html')