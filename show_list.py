# show_list.py
import os
import discord
import requests
from discord.ext import commands
import config


def show_list(viewed):
    return config.collection.find({"viewed": viewed})
