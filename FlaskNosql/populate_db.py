from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = os.getenv('MONGO_PORT', '27017')
MONGO_DB = os.getenv('MONGO_DB', 'Django_Music')

# Construct MongoDB URI with authentication
if MONGO_USER and MONGO_PASSWORD:
    uri = f'mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin'
else:
    uri = f'mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}'

# Connect to MongoDB
client = MongoClient(uri)
db = client[MONGO_DB]

# Clear existing collections
db.composers.drop()
db.pieces.drop()
db.orchestras.drop()
db.conductors.drop()
db.reviews.drop()
db.users.drop()

# Create a test user for reviews
test_user = {
    'username': 'music_critic',
    'password': generate_password_hash('critic123'),
    'is_admin': False
}
user_id = db.users.insert_one(test_user).inserted_id

# Composers
composers = [
    {'name': 'Philip Sparke', 'nationality': 'British'},
    {'name': 'Goff Richards', 'nationality': 'British'},
    {'name': 'James Curnow', 'nationality': 'American'},
    {'name': 'Philip Harper', 'nationality': 'British'},
    {'name': 'Simon Dobson', 'nationality': 'British'},
    {'name': 'Bert Appermont', 'nationality': 'Belgian'},
    {'name': 'Oliver Waespi', 'nationality': 'Swiss'},
    {'name': 'Peter Graham', 'nationality': 'British'},
    {'name': 'Paul Lovatt-Cooper', 'nationality': 'British'},
    {'name': 'Jonathan Bates', 'nationality': 'British'}
]
composer_ids = [str(db.composers.insert_one(composer).inserted_id) for composer in composers]

# Orchestras
orchestras = [
    {'orchestra_name': 'London Symphony Orchestra'},
    {'orchestra_name': 'Berlin Philharmonic'},
    {'orchestra_name': 'Vienna Philharmonic'},
    {'orchestra_name': 'New York Philharmonic'},
    {'orchestra_name': 'Royal Concertgebouw Orchestra'},
    {'orchestra_name': 'Chicago Symphony Orchestra'},
    {'orchestra_name': 'Boston Symphony Orchestra'},
    {'orchestra_name': 'Philadelphia Orchestra'},
    {'orchestra_name': 'Cleveland Orchestra'},
    {'orchestra_name': 'Los Angeles Philharmonic'}
]
orchestra_ids = [str(db.orchestras.insert_one(orchestra).inserted_id) for orchestra in orchestras]

# Conductors
conductors = [
    {'firstname': 'Sir Simon', 'lastname': 'Rattle', 'age': 68},
    {'firstname': 'Gustavo', 'lastname': 'Dudamel', 'age': 42},
    {'firstname': 'Marin', 'lastname': 'Alsop', 'age': 66},
    {'firstname': 'Yannick', 'lastname': 'Nézet-Séguin', 'age': 48},
    {'firstname': 'Andris', 'lastname': 'Nelsons', 'age': 44},
    {'firstname': 'Riccardo', 'lastname': 'Muti', 'age': 81},
    {'firstname': 'Valery', 'lastname': 'Gergiev', 'age': 70},
    {'firstname': 'Franz', 'lastname': 'Welser-Möst', 'age': 63},
    {'firstname': 'Esa-Pekka', 'lastname': 'Salonen', 'age': 64},
    {'firstname': 'Daniel', 'lastname': 'Barenboim', 'age': 80}
]
conductor_ids = [str(db.conductors.insert_one(conductor).inserted_id) for conductor in conductors]

# Assign conductors to orchestras
for i, orchestra_id in enumerate(orchestra_ids):
    db.orchestras.update_one(
        {'_id': ObjectId(orchestra_id)},
        {'$set': {'conductor_id': conductor_ids[i]}}
    )

# Pieces
pieces = [
    {'piece_name': 'Caledonian Suite', 'composer_id': composer_ids[0], 'orchestra_id': orchestra_ids[0], 'era': 'Modern'},
    {'piece_name': 'Day in the Life of a Knight', 'composer_id': composer_ids[1], 'orchestra_id': orchestra_ids[1], 'era': 'Modern'},
    {'piece_name': 'Childhood Hymn', 'composer_id': composer_ids[2], 'orchestra_id': orchestra_ids[2], 'era': 'Modern'},
    {'piece_name': 'Colwell Suite', 'composer_id': composer_ids[3], 'orchestra_id': orchestra_ids[3], 'era': 'Modern'},
    {'piece_name': 'Brief Symphony of Time', 'composer_id': composer_ids[4], 'orchestra_id': orchestra_ids[4], 'era': 'Modern'},
    {'piece_name': 'Brussels Requiem', 'composer_id': composer_ids[5], 'orchestra_id': orchestra_ids[5], 'era': 'Modern'},
    {'piece_name': 'Audivi Media Nocte', 'composer_id': composer_ids[6], 'orchestra_id': orchestra_ids[6], 'era': 'Modern'},
    {'piece_name': 'Aurelia', 'composer_id': composer_ids[7], 'orchestra_id': orchestra_ids[7], 'era': 'Modern'},
    {'piece_name': 'Celtic Suite', 'composer_id': composer_ids[8], 'orchestra_id': orchestra_ids[8], 'era': 'Modern'},
    {'piece_name': 'British Isles Suite', 'composer_id': composer_ids[9], 'orchestra_id': orchestra_ids[9], 'era': 'Modern'},
    {'piece_name': 'Paganini Variations', 'composer_id': composer_ids[0], 'orchestra_id': orchestra_ids[0], 'era': 'Modern'},
    {'piece_name': 'Year of the Dragon', 'composer_id': composer_ids[1], 'orchestra_id': orchestra_ids[1], 'era': 'Modern'},
    {'piece_name': 'Montage', 'composer_id': composer_ids[2], 'orchestra_id': orchestra_ids[2], 'era': 'Modern'},
    {'piece_name': 'Journey into Freedom', 'composer_id': composer_ids[3], 'orchestra_id': orchestra_ids[3], 'era': 'Modern'},
    {'piece_name': 'Dances and Arias', 'composer_id': composer_ids[4], 'orchestra_id': orchestra_ids[4], 'era': 'Modern'},
    {'piece_name': 'Titan\'s Progress', 'composer_id': composer_ids[5], 'orchestra_id': orchestra_ids[5], 'era': 'Modern'},
    {'piece_name': 'Revelation', 'composer_id': composer_ids[6], 'orchestra_id': orchestra_ids[6], 'era': 'Modern'},
    {'piece_name': 'Harmony Music', 'composer_id': composer_ids[7], 'orchestra_id': orchestra_ids[7], 'era': 'Modern'},
    {'piece_name': 'Tallis Variations', 'composer_id': composer_ids[8], 'orchestra_id': orchestra_ids[8], 'era': 'Modern'},
    {'piece_name': 'Cloudcatcher Fells', 'composer_id': composer_ids[9], 'orchestra_id': orchestra_ids[9], 'era': 'Modern'}
]
piece_ids = [str(db.pieces.insert_one(piece).inserted_id) for piece in pieces]

# Reviews
reviews = [
    {
        'text_content': 'A stunning performance of Caledonian Suite by the London Symphony Orchestra. The interpretation was both powerful and nuanced, with exceptional attention to detail in the brass section.',
        'score': 9,
        'date': datetime.now() - timedelta(days=30),
        'user_id': str(user_id),
        'piece_id': piece_ids[0]
    },
    {
        'text_content': 'While technically proficient, the Berlin Philharmonic\'s rendition of Day in the Life of a Knight lacked the emotional depth I was expecting. The brass section was particularly disappointing.',
        'score': 6,
        'date': datetime.now() - timedelta(days=25),
        'user_id': str(user_id),
        'piece_id': piece_ids[1]
    },
    {
        'text_content': 'The Vienna Philharmonic\'s performance of Childhood Hymn was nothing short of magical. The strings were particularly expressive, creating an atmosphere of pure beauty.',
        'score': 10,
        'date': datetime.now() - timedelta(days=20),
        'user_id': str(user_id),
        'piece_id': piece_ids[2]
    },
    {
        'text_content': 'Colwell Suite was performed competently by the New York Philharmonic, but failed to capture the essence of the piece. The interpretation felt somewhat mechanical.',
        'score': 7,
        'date': datetime.now() - timedelta(days=15),
        'user_id': str(user_id),
        'piece_id': piece_ids[3]
    },
    {
        'text_content': 'The Royal Concertgebouw Orchestra\'s rendition of Brief Symphony of Time was a masterclass in orchestral playing. Every section was perfectly balanced, creating a truly immersive experience.',
        'score': 9,
        'date': datetime.now() - timedelta(days=10),
        'user_id': str(user_id),
        'piece_id': piece_ids[4]
    },
    {
        'text_content': 'Brussels Requiem was performed with great sensitivity by the Chicago Symphony Orchestra. The brass section was particularly impressive, with perfect intonation throughout.',
        'score': 8,
        'date': datetime.now() - timedelta(days=5),
        'user_id': str(user_id),
        'piece_id': piece_ids[5]
    },
    {
        'text_content': 'The Boston Symphony Orchestra\'s performance of Paganini Variations was technically brilliant, showcasing the virtuosity of the brass section. A true tour de force.',
        'score': 9,
        'date': datetime.now() - timedelta(days=8),
        'user_id': str(user_id),
        'piece_id': piece_ids[10]
    },
    {
        'text_content': 'Year of the Dragon was given a powerful interpretation by the Philadelphia Orchestra. The dynamic contrasts were particularly effective, though the final movement felt rushed.',
        'score': 8,
        'date': datetime.now() - timedelta(days=12),
        'user_id': str(user_id),
        'piece_id': piece_ids[11]
    },
    {
        'text_content': 'The Cleveland Orchestra\'s Montage was a revelation. The clarity of texture and precision of ensemble playing was exemplary throughout.',
        'score': 9,
        'date': datetime.now() - timedelta(days=15),
        'user_id': str(user_id),
        'piece_id': piece_ids[12]
    },
    {
        'text_content': 'Journey into Freedom by the Los Angeles Philharmonic was a mixed bag. While the brass section shone, the strings lacked the necessary weight in the climaxes.',
        'score': 7,
        'date': datetime.now() - timedelta(days=18),
        'user_id': str(user_id),
        'piece_id': piece_ids[13]
    }
]

for review in reviews:
    db.reviews.insert_one(review)

print("Database populated successfully!") 