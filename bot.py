# bot.py
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from update_list import add_movie, check_movie_in_list
from update_list import check_movie_in_any_list, remove_movie
from show_list import show_list
from set_viewed import set_viewed
from poll import create_poll

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='--')


@bot.command(name='poll', help='Select 10 random movies and create a poll.' +
             'Default time 60 min, max 1440')
async def poll(ctx, num_minutes: int = 60):
    if num_minutes > 1440:
        num_minutes = 1440
    if num_minutes == 1:
        response = f'Setting a poll for {num_minutes} minute'
    else:
        response = f'Setting a poll for {num_minutes} minutes'

    response += "\n @here poll is starting"
    await ctx.send(response)

    response = create_poll(num_minutes)

    await ctx.send("```" + response + "```")


@bot.command(name='add', help='Add movie to the watch list. IMDB link only.')
async def add(ctx, link: str):
    if "imdb.com" in link:
        imdb_id = link.split("title/")[1].split("/")[0]
        if check_movie_in_list(imdb_id, viewed=False) is None:
            add_movie(imdb_id, ctx.author.name)
            response = "Movie was added to the list."
        else:
            response = "Movie is already in the list."
    else:
        response = "Please provide valid IMDB link."
    await ctx.send(response)


@bot.command(name='list', help='Current unwatched movies.')
async def list(ctx):
    response = show_list(viewed=False)
    movie_list = ""
    for movie in response:
        movie_list = movie_list + \
            movie['title'] + " (" + movie['year'] + \
            "), submitted by @" + movie['submitter'] + "\n"
    await ctx.send("```" + "Unviewed Movies \n" + movie_list + "```")


@bot.command(name='viewedlist', help='Current watched movies.')
async def viewedlist(ctx):
    response = show_list(viewed=True)
    print(response)
    movie_list = ""
    for movie in response:
        movie_list = movie_list + movie['title'] + " (" + movie['year'] + \
            "), submitted by @" + \
            movie['submitter'] + ", viewed on " + \
            str(movie['viewedDate']).split(" ")[0] + "\n"
    if movie_list == "":
        await ctx.send("No movies have been viewed yet.")
    else:
        await ctx.send("```" + "Viewed Movies \n" + movie_list + "```")


@bot.command(name='setviewed', help='Put movie in viewed list. IMDB link only')
async def setviewed(ctx, link):
    if "imdb.com" in link:
        imdb_id = link.split("title/")[1].split("/")[0]
        if check_movie_in_any_list(imdb_id) is None:
            response = "Can't set movie to viewed, not in watchlist."
        elif check_movie_in_list(imdb_id, viewed=True) is None:
            set_viewed(imdb_id)
            response = "Movie was added to the viewed list."
        else:
            response = "Movie is already in viewed list."
    else:
        response = "Please provide valid IMDB link."
    await ctx.send(response)


@bot.command(name='remove', help='Remove from watch list. IMDB link only.')
async def remove(ctx, link: str):
    if "imdb.com" in link:
        imdb_id = link.split("title/")[1].split("/")[0]
        if check_movie_in_list(imdb_id, viewed=False):
            remove_movie(imdb_id)
            response = "Movie was removed from the list."
        else:
            response = "Movie is already not in the list."
    else:
        response = "Please provide valid IMDB link."
    await ctx.send(response)

bot.run(TOKEN)
