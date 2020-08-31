# poll.py
import config
import random
from discord import Embed


def create_poll(num_minutes):
    all_movies = list(config.collection.find({"viewed": False}))

    poll_list = []
    movie_map = {}

    if len(all_movies) > 10:
        poll_list = random.sample(all_movies, k=10)
    

    embed = Embed(title = "The poll has begun!")
    embedded_messages = []
    movie_list = ""
    number = 1
    for movie in poll_list:
        string_build = f"""**[{number}.  {movie['Title']}](https://www.imdb.com/title/{movie['imdbID']})** submitted by {movie['submitter']}\n
        **Release Date:** {movie['Released']} **Runtime:** {movie['Runtime']} **Rating:** {movie['rtScore']}\n\n"""
        if len(movie_list) + len(string_build) > 2048:
            embed.description = movie_list
            embedded_messages.append(embed)
            movie_list = ""
            embed = Embed(title = "Submitted Movies (Cont...)")
        movie_list += string_build
        movie['votes'] = 0
        movie_map[number] = movie
        number += 1
    embed.description = movie_list
    embedded_messages.append(embed)

    return embedded_messages, movie_map


def tiebreak(movies):
    poll_list_with_indexes = []
    for index, movie in enumerate(movies, start=1):
        current_movie_str = str(index) + ") " + movie
        poll_list_with_indexes.append(current_movie_str)
    poll_list_str = ""
    for movie in poll_list_with_indexes:
        poll_list_str += movie + "\n"

    return poll_list_str


def poll_to_dict(poll_str):
    poll_dict = {}
    movie_list = list(filter(bool, poll_str.splitlines()))
    for movie in movie_list:
        poll_dict[str(movie.split(')')[0])] = {'Title':
                                               movie.split('(')[0].split(')')[
                                                   1].strip(),
                                               'votes': 0}

    return poll_dict
