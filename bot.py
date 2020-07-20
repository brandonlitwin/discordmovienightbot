# bot.py
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from update_list import add_movie, check_movie_in_list
from update_list import check_movie_in_any_list, remove_movie
from show_list import show_list
from set_viewed import set_viewed
from poll import create_poll, poll_to_dict

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='--')

current_poll_dict = {}


@bot.command(name='poll', help='Select 10 random movies and create a poll. ' +
             'Default time 60 min, max 1440')
async def poll(ctx, num_minutes: int = 60):
    if num_minutes > 1440:
        num_minutes = 1440
    if num_minutes == 1:
        response = f'Setting a poll for {num_minutes} minute'
    else:
        response = f'Setting a poll for {num_minutes} minutes'

    # send initial message
    response += "\n @everyone poll is starting, use vote command to vote"
    await ctx.send(response)

    # get all the movies of the poll
    response = create_poll(num_minutes)

    # call function to convert str to dict
    global current_poll_dict
    current_poll_dict = poll_to_dict(response)

    # send poll
    message = await ctx.send("```" + response + "```")
    """emojis = ['1\u20E3', '2\u20E3', '3\u20E3', '4\u20E3', '5\u20E3',
              '6\u20E3', '7\u20E3', '8\u20E3', '9\u20E3', '\U0001f51f']

    # add emojis
    for emoji in emojis:
        await message.add_reaction(emoji)"""


@bot.command(name='vote', help='Cast your votes in order from first to third' +
             ' pick. Use the number labels generated by the poll.')
async def vote(ctx, first_pick: str, second_pick: str, third_pick: str):
    max_poll_id = len(current_poll_dict) + 1
    if (first_pick == second_pick or first_pick == third_pick or
            second_pick == third_pick):
        response = 'Please do not vote for the same movie multiple times.'
    elif (not 0 < int(first_pick) < max_poll_id or
          not 0 < int(second_pick) < max_poll_id or
          not 0 < int(third_pick) < max_poll_id):
        response = 'Please make sure all votes match a number on the poll.'
    else:
        try:
            response = f'Thank you for the vote @{ctx.author.name}.'

            first_pick_current_votes = int(
                current_poll_dict[first_pick]['votes'])
            second_pick_current_votes = int(
                current_poll_dict[second_pick]['votes'])
            third_pick_current_votes = int(
                current_poll_dict[third_pick]['votes'])

            current_poll_dict[first_pick]['votes'] = first_pick_current_votes + 3

            current_poll_dict[second_pick]['votes'] = second_pick_current_votes + 2

            current_poll_dict[third_pick]['votes'] = third_pick_current_votes + 1
        except:
            response = 'Please vote for 3 movies with correct format ' + \
             '(3 numbers [first_pick] [second_pick] [third_pick])'

    await ctx.send(response)
    print(current_poll_dict)


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
