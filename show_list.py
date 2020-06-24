#show_list.py
import os
import discord
import requests
from discord.ext import commands
import config

def show_list(viewed):
  for post in config.collection.find({"viewed": viewed}):
    print(post)
  return config.collection.find({"viewed": viewed})
