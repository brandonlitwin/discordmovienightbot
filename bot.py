# bot.py
import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!movie')

@bot.command(name='poll', help='Select 10 random movies and create a poll. Default time 60 min, max 1440')
async def poll(ctx, num_minutes: int=60):
    if num_minutes > 1440:
        num_minutes = 1440
    if num_minutes == 1:
        response = f'Setting a poll for {num_minutes} minute'
    else:
        response = f'Setting a poll for {num_minutes} minutes'
    await ctx.send(response)

@bot.command(name='add', help='Add movie to the watch list. IMDB link only.')
async def add(ctx, link: str):
    response = "Movie will be added to the list."
    await ctx.send(response)

@bot.command(name='list', help='Current unwatched movies')
async def list(ctx, link: str):
    response = "This is the list of watched movies."
    await ctx.send(response)

@bot.command(name='viewedlist', help='Current watched movies')
async def viewedlist(ctx, link: str):
    response = "This is the list of viewed movies."
    await ctx.send(response)

@bot.command(name='remove', help='Remove from watch list. IMDB link only.')
async def remove(ctx, link: str):
    response = "Movie will be removed from the list."
    await ctx.send(response)

bot.run(TOKEN)
