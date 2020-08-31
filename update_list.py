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
    print(config.collection.find_one({"Title": title, "viewed": viewed}))
    return config.collection.find_one({"Title": title, "viewed": viewed})


def check_movie_title_in_any_list(title):
    print(title)
    print(config.collection.find_one({"Title": title}))
    return config.collection.find_one({"Title": title})


def add_movie_id(imdb_id, submitter):
    data = search_omdb_id(imdb_id)
    print(data)

    if data:
        # try to get RT rating
        print("data was found for movie")
        try:
            rating = data['Ratings'][1]['Value']
        except IndexError:
            rating = "n/a"
        post = {"imdbID": imdb_id,
                "Title": data['Title'],
                "Released": data['Year'],
                "rtScore": rating,
                "Runtime": data['Runtime'],
                "Plot": data['Plot'],
                "submitter": submitter,
                "viewed": False,
                "viewedDate": None,
                "Poster": data['Poster']}
        config.collection.insert_one(post)
        return True
    else:
        return False


def search_movie_title(title):
    data = search_omdb_title(title)
    return data


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
                "Title": data['Title'],
                "Released": data['Year'],
                "rtScore": rating,
                "Runtime": data['Runtime'],
                "Plot": data['Plot'],
                "submitter": submitter,
                "viewed": False,
                "viewedDate": None,
                "Poster": data['Poster']}
        config.collection.insert_one(post)
        return True
    else:
        return False


def remove_movie_id(imdb_id):
    config.collection.find_one_and_delete({"imdbID": imdb_id})


def remove_movie_title(title):
    config.collection.find_one_and_delete({"title": title})


def search_omdb_id(imdb_id):
    url = 'http://www.omdbapi.com/?i=' + imdb_id + "&apikey=" + config.API_KEY
    print(url)
    r = requests.get(url=url)
    data = r.json()
    if data['Response'] == 'False':
        return False
    else:
        return data


def search_omdb_title(title):
    url = 'http://www.omdbapi.com/?t=' + title + "&apikey=" + config.API_KEY
    print(url)
    r = requests.get(url=url)
    data = r.json()
    if data['Response'] == 'False':
        return False
    else:
        return data
