import os
import urllib.parse
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient

load_dotenv()
REQUEST_URL = os.getenv('OMDB_REQUEST_URL')
API_KEY = os.getenv('OMDB_API_KEY')

USERNAME = urllib.parse.quote_plus(os.getenv('CONNECTION_USER'))
PASSWORD = urllib.parse.quote_plus(os.getenv('CONNECTION_PASSWORD'))

CONNECTION_STRING = f'mongodb+srv://{USERNAME}:{PASSWORD}@movienightbot-dttqs.mongodb.net/test'

cluster = MongoClient(CONNECTION_STRING)
db = cluster["MovieNightBot"]
collection = db["movies"]
autoview = True
