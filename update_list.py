# update_list.py
import os
import discord
import requests
from discord.ext import commands
import config


def check_movie_id_in_list(imdb_id, viewed):
    print(imdb_id)
    print(config.collection.find_one({"imdbID": imdb_id, "viewed": viewed}))
    return config.collection.find_one({"imdbID": imdb_id, "viewed": viewed})


def check_movie_id_in_any_list(imdb_id):
    print(imdb_id)
    print(config.collection.find_one({"imdbID": imdb_id}))
    return config.collection.find_one({"imdbID": imdb_id})


def check_movie_title_in_list(title, viewed):
    print(title)
    print(config.collection.find_one({"title": title, "viewed": viewed}))
    return config.collection.find_one({"title": title, "viewed": viewed})


def check_movie_title_in_any_list(title):
    print(title)
    print(config.collection.find_one({"title": title}))
    return config.collection.find_one({"title": title})


def add_movie_id(imdb_id, submitter):
    data = search_omdb(imdb_id)
    print(data)

    if data:
        # try to get RT rating
        print("data was found for movie")
        try:
            rating = data['Ratings'][1]['Value']
        except IndexError:
            rating = "n/a"
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
        return True
    else:
        return False


def search_movie_title(title):
    data = search_omdb_title(title)
    print(data)
    if data:
        link = "https://www.imdb.com/title/" + data['imdbID']
        return link
    else:
        return False


def add_movie_title(title, submitter):
    data = search_omdb_title(title)
    print(data)

    if data:
        # try to get RT rating
        print("data was found for movie")
        try:
            rating = data['Ratings'][1]['Value']
        except IndexError:
            rating = "n/a"
        post = {"imdbID": data['imdbID'],
                "title": data['Title'],
                "year": data['Year'],
                "rtScore": rating,
                "runtime": data['Runtime'],
                "plot": data['Plot'],
                "submitter": submitter,
                "viewed": False,
                "viewedDate": None}
        config.collection.insert_one(post)
        return True
    else:
        return False


def remove_movie_id(imdb_id):
    config.collection.find_one_and_delete({"imdbID": imdb_id})


def remove_movie_title(title):
    config.collection.find_one_and_delete({"title": title})


def search_omdb_id(imdb_id):
    url = 'http://www.omdbapi.com/?i=' + imdb_id + config.API_KEY
    r = requests.get(url=url)
    data = r.json()
    if data['Response'] == 'False':
        return False
    else:
        return data


def search_omdb_title(title):
    url = 'http://www.omdbapi.com/?t=' + title + config.API_KEY
    r = requests.get(url=url)
    data = r.json()
    if data['Response'] == 'False':
        return False
    else:
        return data
