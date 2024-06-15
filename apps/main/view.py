from flask import Blueprint, render_template, g
from extensions import Movie

blueprint = Blueprint("main", __name__)

@blueprint.route("/")
def index():
    movie = Movie()
    top_movies = movie.top(g.db, 25)
    recent_movies = movie.recent(g.db, 25)
    random_movies = movie.random_movie(g.db, 25)

    return render_template("/main/index.html", top = top_movies, recent = recent_movies, random = random_movies)