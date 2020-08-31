import os
import urllib.parse
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient

load_dotenv()
API_KEY = os.getenv('OMDB_API_KEY')
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = os.getenv('CHANNEL_ID')
SERVER = os.getenv('SERVER_ID')

CONNECTION_STRING = 'localhost'

cluster = MongoClient(CONNECTION_STRING)
db = cluster["MovieNightBot"]
collection = db["movies"]
autoview = True
tiebreak_num_seconds = 300
autopoll_schedule = '2000-01-01 12:00:00'
