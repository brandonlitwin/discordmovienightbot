#poll.py
import config
import random

def create_poll(num_minutes):
  unviewed_movies = []
  for post in config.collection.find({"viewed": False}):
    current_movie_str = str(post['title']) + " (https://imdb.com/title/" + str(post['imdbID']) + "), submitted by @" + str(post['submitter']) + "\n"
    unviewed_movies.append(current_movie_str) # + str(post['title']) + " (https://imdb.com/title/" + str(post['imdbID']) + "), submitted by @" + str(post['submitter']) + "\n"

  poll_list = unviewed_movies

  if len(unviewed_movies) > 10:
    poll_list = random.sample(unviewed_movies, k=10)

  poll_list_str = ""

  for movie in poll_list:
    poll_list_str += movie + "\n"

  return poll_list_str
