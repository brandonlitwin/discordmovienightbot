import os
import discord
import requests
from dotenv import load_dotenv
from discord.ext import commands
from datetime import date
import pymongo
from pymongo import MongoClient
import urllib.parse

load_dotenv()
REQUEST_URL = os.getenv('OMDB_REQUEST_URL')
API_KEY = os.getenv('OMDB_API_KEY')

USERNAME = urllib.parse.quote_plus(os.getenv('CONNECTION_USER'))
PASSWORD = urllib.parse.quote_plus(os.getenv('CONNECTION_PASSWORD'))

CONNECTION_STRING = f'mongodb+srv://{USERNAME}:{PASSWORD}@movienightbot-dttqs.mongodb.net/test'

cluster = MongoClient(CONNECTION_STRING)
db = cluster["MovieNightBot"]
collection = db["movies"]

def add_movie(imdb_link, submitter):
  imdb_id = imdb_link.split("title/")[1].split("/")[0]
  data = search_omdb(imdb_id)
  print(data['Ratings'][1]['Value'])
  if data:
    post = {"imdbID": imdb_id,
            "title": data['Title'],
            "year": data['Year'],
            "rtScore": data['Ratings'][1]['Value'],
            "runtime": data['Runtime'],
            "plot": data['Plot'],
            "submitter": submitter,
            "viewed": False,
            "viewedDate": None}
    
    collection.insert_one(post)

def search_omdb(imdb_id):
  url = REQUEST_URL + imdb_id + API_KEY
  r = requests.get(url=url)
  data = r.json() 
  print(data['Title'])
  print(data['Year'])
  return data