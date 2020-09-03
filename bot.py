# bot.py
import config
import datetime
import os
import discord
import asyncio
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord import Embed
from update_list import add_movie_id, check_movie_id_in_list
from update_list import check_movie_id_in_any_list, remove_movie_id
from update_list import add_movie_title, check_movie_title_in_list
from update_list import check_movie_title_in_any_list, remove_movie_title
from update_list import search_movie_title
from embed_builder import build_movie_embed
from show_list import show_list
from set_viewed import set_viewed_by_id, set_viewed_by_title
from poll import create_poll, poll_to_dict, tiebreak

load_dotenv()

client = discord.Client()

bot = commands.Bot(command_prefix='!')

current_poll_dict = {}

poll_running = False

users_who_voted = []


@bot.command(name='toggleautoview', help='Toggle autoview of movies after poll is done.')
async def toggleautoview(ctx):
    config.autoview = not config.autoview
    response = f"Autoview has been set to {config.autoview}"
    await ctx.send("```" + response + "```")


@tasks.loop(hours=168.0)
async def autopoll():
    print('in loop')
    print('running autopoll')
    channel = bot.get_channel(int(config.CHANNEL))
    global poll_running
    global users_who_voted
    poll_running = True
    num_minutes = 1440
    ctx = channel
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

    # send results on poll end
    poll_time_seconds = num_minutes * 60
    print(poll_time_seconds)
    await asyncio.sleep(poll_time_seconds)

    print("poll is done")
    poll_running = False
    users_who_voted.clear()

    # get max value
    reformatted_dict = {}
    for key, val in current_poll_dict.items():
        reformatted_dict[val['Title']] = val['votes']
    most_votes = max(reformatted_dict.values())
    keys = [key for key, value in reformatted_dict.items() if value == most_votes]
    import random
    if len(keys) > 1:
        emojis = ['1\u20E3', '2\u20E3', '3\u20E3', '4\u20E3', '5\u20E3',
                '6\u20E3', '7\u20E3', '8\u20E3', '9\u20E3', '\U0001f51f']
        emojis = emojis[:len(keys)]
        # add emojis
        tiebreak_message = f"There was a tie of {most_votes} votes between {len(keys)} movies \n" + \
            "@everyone Please vote for the tiebreaker. You have 5 minutes. \n" + \
            "and if you tie again, I'll pick one myself :)"

        # Create tiebreak poll
        await ctx.send(tiebreak_message)
        tiebreak_poll = tiebreak(keys)
        tiebreak_poll_message = await ctx.send("```" + tiebreak_poll + "```")
        tiebreak_poll_message_id = tiebreak_poll_message.id
        for emoji in emojis:
            await tiebreak_poll_message.add_reaction(emoji)
        await asyncio.sleep(config.tiebreak_num_seconds)
        tiebreak_poll_message = await ctx.fetch_message(tiebreak_poll_message_id)
        # Count tiebreak reactions
        tiebreak_reactions = {}
        for reaction in tiebreak_poll_message.reactions:
            tiebreak_reactions[reaction.emoji] = reaction.count
        print(tiebreak_reactions)
        most_votes = max(tiebreak_reactions.values())
        tiebreak_keys = [key for key, value in tiebreak_reactions.items() if value == most_votes]
        # Tied again, just pick a random from the tiebreak poll
        if len(tiebreak_keys) > 1:
            winner = random.choice(keys)
            poll_results = "Tiebreak is now completed \n" + \
                f"There was another tie zzz \n" + \
                f"Since you can't decide, I've decided that the winner is {winner}"
        else:
            winner = keys[emojis.index(tiebreak_keys[0])]
            poll_results = f"Tie is broken, and the winner is {winner}!"

    else:
        winner = keys[0]
        poll_results = "Poll is now completed \n" + f"Winner is {winner}" + \
        f" with {most_votes} votes!"

    # if autoview on, set winner to viewed
    if config.autoview:
        config.collection.find_one_and_update({"Title": winner}, {'$set': {'viewed': True, 'viewedDate': datetime.datetime.utcnow()}})

    await ctx.send("```" + poll_results + "```")


@autopoll.before_loop
async def wait_to_start_autopoll():
    print('before loop')
    import pytz
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    current_time_str = utc_now
    print(config.autopoll_schedule, current_time_str)
    time_diff = config.autopoll_schedule - current_time_str
    print(time_diff.total_seconds())
    if time_diff.total_seconds() > 0:
        await asyncio.sleep(time_diff.total_seconds())


@bot.command(name='poll', help='Select 10 random movies and create a poll. ' +
             'Default time 1440 min (24 hours)')
async def poll(ctx, num_minutes: int = 1440):
    print('starting poll')
    global poll_running
    global users_who_voted
    poll_running = True
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

    # send results on poll end
    poll_time_seconds = num_minutes * 60
    print(poll_time_seconds)
    await asyncio.sleep(poll_time_seconds)

    print("poll is done")
    poll_running = False
    users_who_voted.clear()

    # get max value
    reformatted_dict = {}
    for key, val in current_poll_dict.items():
        reformatted_dict[val['Title']] = val['votes']
    most_votes = max(reformatted_dict.values())
    keys = [key for key, value in reformatted_dict.items() if value == most_votes]
    import random
    if len(keys) > 1:
        emojis = ['1\u20E3', '2\u20E3', '3\u20E3', '4\u20E3', '5\u20E3',
                  '6\u20E3', '7\u20E3', '8\u20E3', '9\u20E3', '\U0001f51f']
        emojis = emojis[:len(keys)]
        # add emojis
        tiebreak_message = f"There was a tie of {most_votes} votes between {len(keys)} movies \n" + \
            "@everyone Please vote for the tiebreaker. You have 5 minutes. \n" + \
            "and if you tie again, I'll pick one myself :)"

        # Create tiebreak poll
        await ctx.send(tiebreak_message)
        tiebreak_poll = tiebreak(keys)
        tiebreak_poll_message = await ctx.send("```" + tiebreak_poll + "```")
        tiebreak_poll_message_id = tiebreak_poll_message.id
        for emoji in emojis:
            await tiebreak_poll_message.add_reaction(emoji)
        await asyncio.sleep(config.tiebreak_num_seconds)
        tiebreak_poll_message = await ctx.fetch_message(tiebreak_poll_message_id)
        # Count tiebreak reactions
        tiebreak_reactions = {}
        for reaction in tiebreak_poll_message.reactions:
            tiebreak_reactions[reaction.emoji] = reaction.count
        print(tiebreak_reactions)
        most_votes = max(tiebreak_reactions.values())
        tiebreak_keys = [key for key, value in tiebreak_reactions.items() if value == most_votes]
        # Tied again, just pick a random from the tiebreak poll
        if len(tiebreak_keys) > 1:
            winner = random.choice(keys)
            poll_results = "Tiebreak is now completed \n" + \
                f"There was another tie zzz \n" + \
                f"Since you can't decide, I've decided that the winner is {winner}"
        else:
            winner = keys[emojis.index(tiebreak_keys[0])]
            poll_results = f"Tie is broken, and the winner is {winner}!"

    else:
        winner = keys[0]
        poll_results = "Poll is now completed \n" + f"Winner is {winner}" + \
        f" with {most_votes} votes!"

    # if autoview on, set winner to viewed
    if config.autoview:
        config.collection.find_one_and_update({"Title": winner}, {'$set': {'viewed': True, 'viewedDate': datetime.datetime.utcnow()}})
    winning_movie = config.collection.find_one({"Title": winner})
    embed = build_movie_embed(winning_movie, poll_results)
    await ctx.send(embed = embed)


@bot.command(name='schedule', help='Schedule poll')
async def schedule(ctx, datetime_str: str):
    from dateutil.parser import parse
    from dateutil.tz import UTC
    schedule_datetime = parse(datetime_str)
    message = f"Poll is scheduled for {schedule_datetime}"
    schedule_datetime = schedule_datetime.astimezone(UTC)
    print(schedule_datetime, type(schedule_datetime))
    await ctx.send("```" + message + "```")
    config.autopoll_schedule = schedule_datetime
    print(config.autopoll_schedule)
    print('autopoll start')
    autopoll.start()


@bot.command(name='vote', help='Cast your votes in order from first to third' +
             ' pick. Use the number labels generated by the poll.' +
             ' Can choose to pick only one, two, or three movies.')
async def vote(ctx, *picks):
    if not poll_running:
        response = "There is no poll active, sorry!"
    elif ctx.author.mention in users_who_voted:
        response = f"You have already voted in this poll, {ctx.author.mention}."
    else:
        max_poll_id = len(current_poll_dict) + 1
        actual_picks = []
        # Filter input into valid picks, no more than 3 allowed
        for pick in picks:
            if 0 < int(pick) < max_poll_id:
                if len(actual_picks) < 4:
                    actual_picks.append(pick)

        # Add votes of actual picks to totals
        num_picks = len(actual_picks)
        if num_picks > 0:
            first_pick = actual_picks[0]
            current_poll_dict[first_pick]['votes'] = int(current_poll_dict[first_pick]['votes']) + 3
            if num_picks > 1:
                second_pick = actual_picks[1]
                current_poll_dict[second_pick]['votes'] = int(current_poll_dict[second_pick]['votes']) + 2
                if num_picks > 2:
                    third_pick = actual_picks[2]
                    current_poll_dict[third_pick]['votes'] = int(current_poll_dict[third_pick]['votes']) + 1

            response = f'Thank you for the vote {ctx.author.mention}.'
            users_who_voted.append(ctx.author.mention)
            print(users_who_voted)
        else:
            response = f"Could not read any picks. Please try again, {ctx.author.mention}."

    await ctx.send(response)
    print(current_poll_dict)
    # get highest 3 votes
    reformatted_dict = {}
    for key, val in current_poll_dict.items():
        reformatted_dict[val['Title']] = val['votes']
    sorted_dict = sorted(reformatted_dict.items(), key=lambda x: x[1], reverse=True)
    embed = Embed(title='Poll Status')
    embed.add_field(name=f"{sorted_dict[0][0]}", value=f"{sorted_dict[0][1]} votes", inline=True)
    embed.add_field(name=f"{sorted_dict[1][0]}", value=f"{sorted_dict[1][1]} votes", inline=True)
    embed.add_field(name=f"{sorted_dict[2][0]}", value=f"{sorted_dict[2][1]} votes", inline=True)
    response = await ctx.send(embed=embed)

@bot.command(name='add', help='Add movie to the watch list. IMDB link or title accepted. Title must be in quotes.')
async def add(ctx, *args):
    movie = ' '.join(args)
    if "imdb.com" in movie:
        imdb_id = movie.split("title/")[1].split("/")[0]
        if check_movie_id_in_list(imdb_id, viewed=False) is None:
            if add_movie_id(imdb_id, ctx.author.mention):
                response = f"{movie} was added to the list."
            else:
                response = f"{movie} could not be added, double check the URL."
        else:
            response = f"{movie} is already in the list."
    else:
        # add by title
        if check_movie_title_in_list(movie, viewed=False) is None:
            found_movie = search_movie_title(movie)
            if found_movie:
                # add rtScore value for ease of access and to mirror DB
                found_movie['rtScore'] = found_movie["Ratings"][1]['Value']
                found_movie['submitter'] = ctx.author.mention
                embed = build_movie_embed(found_movie, "Is this the movie you were looking for?")
                message = await ctx.send(embed=embed)
                message_id = message.id
                emojis = ['\U00002705', '\U0000274c']
                for emoji in emojis:
                    await message.add_reaction(emoji)
                await asyncio.sleep(20)
                # Count reactions
                message = await ctx.fetch_message(message_id)
                reactions = {}
                for reaction in message.reactions:
                    reactions[reaction.emoji] = reaction.count
                print(reactions)
                if reactions['\U00002705'] > reactions['\U0000274c']:
                    # Add movie as it was accepted by user
                    if add_movie_title(movie, ctx.author.mention):
                        response = f"{movie} was added to the watchlist."
                    else:
                        response = "Movie could not be added. Please try again."
                else:
                    response = "Movie will not be added. Try another movie or try adding an IMDB link."
            else:
                response = f"{movie} could not be added. Double check the title or try adding an IMDB link."
        else:
            response = f"{movie} is already in the list."
    await ctx.send(response)


@bot.command(name='bulkadd', help='Add group of movies. IMDB links or titles accepted. Titles must be in quotes.')
async def bulkadd(ctx, *movies):
    response = ""
    for movie in movies:
        if "imdb.com" in movie:
            imdb_id = movie.split("title/")[1].split("/")[0]
            if check_movie_id_in_list(imdb_id, viewed=False) is None:
                if add_movie_id(imdb_id, ctx.author.mention):
                    response += f"{movie} was added to the list.\n"
                else:
                    response += f"{movie} could not be added, double check the URL.\n"
            else:
                response += f"{movie} is already in the list.\n"
        else:
            # add by title
            if check_movie_title_in_list(movie, viewed=False) is None:
                if add_movie_title(movie, ctx.author.mention):
                    response += f"{movie} was added to the list.\n"
                else:
                    response += f"{movie} could not be added. Double check the title or try adding an IMDB link.\n"
            else:
                response += f"{movie} is already in the list.\n"
    await ctx.send(response)


@bot.command(name='list', help='Current unwatched movies.')
async def list(ctx):
    embedded_messages = []
    response = show_list(viewed=False)
    embed = Embed(title = "Movie Watchlist")
    movie_list = ""
    number = 1
    for movie in response:
        string_build = f"""**[{number}.  {movie['Title']}](https://www.imdb.com/title/{movie['imdbID']})** submitted by {movie['submitter']}\n
        **Release Date:** {movie['Released']} **Runtime:** {movie['Runtime']} **Rating:** {movie['rtScore']}\n\n"""
        if len(movie_list) + len(string_build) > 2048:
            embed.description = movie_list
            embedded_messages.append(embed)
            movie_list = ""
            embed = Embed(title = "Submitted Movies (Cont...)")
        movie_list += string_build
        number += 1
    embed.description = movie_list
    embedded_messages.append(embed)
    for message in embedded_messages:
        await ctx.send(embed = message)


@bot.command(name='viewedlist', help='Current watched movies.')
async def viewedlist(ctx):
    response = show_list(viewed=True)
    embed = Embed(title = "Viewed Movies")
    number = 1
    movie_list = ""
    embedded_messages = []
    for movie in response:
        string_build = f"""**[{number}.  {movie['Title']}](https://www.imdb.com/title/{movie['imdbID']})** submitted by {movie['submitter']}\n
        **Release Date:** {movie['Released']} **Runtime:** {movie['Runtime']} **Rating:** {movie['rtScore']} **Viewed on:** {movie['viewedDate'].strftime("%B %d %Y")}\n\n"""
        if len(movie_list) + len(string_build) > 2048:
            embed.description = movie_list
            embedded_messages.append(embed)
            movie_list = ""
            embed = Embed(title = "Viewed Movies (Cont...)")
        movie_list += string_build
        number += 1
    embed.description = movie_list
    embedded_messages.append(embed)
    for message in embedded_messages:
        await ctx.send(embed = message)


@bot.command(name='setviewed', help='Put movie in viewed list. IMDB link or title accepted. Title must be in quotes.')
async def setviewed(ctx, movie):
    if "imdb.com" in movie:
        imdb_id = movie.split("title/")[1].split("/")[0]
        if check_movie_id_in_any_list(imdb_id) is None:
            response = "Can't set movie to viewed, not in watchlist."
        elif check_movie_id_in_list(imdb_id, viewed=True) is None:
            set_viewed_by_id(imdb_id)
            response = "Movie was added to the viewed list."
        else:
            response = "Movie is already in viewed list."
    else:
        # Set viewed by title
        if check_movie_title_in_any_list(movie) is None:
            response = "Can't set movie to viewed. If it is in the unviewed list, try checking spelling with exact quotes or try IMDB link."
        elif check_movie_title_in_list(movie, viewed=True) is None:
            set_viewed_by_title(movie)
            response = "Movie was added to the viewed list."
        else:
            response = "Movie is already in viewed list."

    await ctx.send(response)


@bot.command(name='remove', help='Remove from watch list. IMDB links or titles accepted. Title must be in quotes.')
async def remove(ctx, movie: str):
    if "imdb.com" in movie:
        imdb_id = movie.split("title/")[1].split("/")[0]
        if check_movie_id_in_list(imdb_id, viewed=False):
            remove_movie_id(imdb_id)
            response = "Movie was removed from the list."
        else:
            response = "Movie could not be removed. IMDB id was not found in the list."
    else:
        # Remove by title
        if check_movie_title_in_list(movie, viewed=False):
            remove_movie_title(movie)
            response = "Movie was removed from the list."
        else:
            response = "Movie could not be removed. Double check the title in the list."
    await ctx.send(response)

bot.run(config.TOKEN)
