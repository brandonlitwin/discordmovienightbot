import discord
from discord import Embed
from discord import Color

def build_movie_embed(movie, subtitle=False):
    embed = Embed(title = movie['Title'], url = "https://www.imdb.com/title/" + movie['imdbID'], description = movie['Plot'], color = Color(value=int('af92a5', 16)))
    embed.set_image(url = movie['Poster'])
    embed.add_field(name = "Release Date", value = movie['Released'])
    embed.add_field(name = "Runtime", value = movie['Runtime'])
    embed.add_field(name = "Rating", value = movie['rtScore'] + "🍅")
    embed.add_field(name = "Submitted By", value = movie['submitter'])
    if subtitle:
        embed.set_author(name = subtitle)
    return embed