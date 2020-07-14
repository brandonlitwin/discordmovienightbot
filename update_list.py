#update_list.py
import os
import discord
import requests
from discord.ext import commands
import config


def check_movie_in_list(imdb_id, viewed):
  print(imdb_id)
  print(config.collection.find_one({"imdbID": imdb_id, "viewed": viewed}))
  return config.collection.find_one({"imdbID": imdb_id, "viewed": viewed})

def check_movie_in_any_list(imdb_id):
  print(imdb_id)
  print(config.collection.find_one({"imdbID": imdb_id}))
  return config.collection.find_one({"imdbID": imdb_id})

def add_movie(imdb_id, submitter):
  data = search_omdb(imdb_id)
  # try to get RT rating
  try:
    rating = data['Ratings'][1]['Value']
  except IndexError:
    rating = "n/a"

  if data:
    post = {"imdbID": imdb_id,
            "title": data['Title'],
            "year": data['Year'],
            "rtScore": rating,
            "runtime": data['Runtime'],
            "plot": data['Plot'],
            "submitter": submitter,
            "viewed": False,
            "viewedDate": None}
    
    config.collection.insert_one(post)

def remove_movie(imdb_id):
  config.collection.find_one_and_delete({"imdbID": imdb_id})

def search_omdb(imdb_id):
  url = config.REQUEST_URL + imdb_id + config.API_KEY
  r = requests.get(url=url)
  data = r.json() 
  print(data['Title'])
  print(data['Year'])
  return data