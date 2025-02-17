from mongoengine import *
import datetime
class Conductor(Document):
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    country = StringField(max_length=50)
    orchestra_id  = None
    conductor_id = ObjectIdField(required=True, unique=True, primary_key=True)
class Orchestra(Document):
    name = StringField(max_length=50)
    orchestra_id = ObjectIdField(required=True, unique=True, primary_key=True)
