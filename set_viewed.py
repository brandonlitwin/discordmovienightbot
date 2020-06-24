#set_viewed.py
import os
import discord
import requests
from discord.ext import commands
import config
import datetime

def set_viewed(imdb_id):
  return config.collection.find_one_and_update({"imdbID": imdb_id}, {'$set': {'viewed': True, 'viewedDate': datetime.datetime.utcnow()}})
