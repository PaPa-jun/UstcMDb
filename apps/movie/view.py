from flask import Blueprint, render_template, g
from extensions import Movie

blueprint = Blueprint("movie", __name__)

@blueprint.route("/top25")
def top25():
    movie = Movie()
    movies = movie.top(g.db, 25)

    return render_template("movie/top.html", movies_info = movies)

@blueprint.route("/<id>")
def movie_detail(id):
    movie = Movie()
    current_movie = movie.get_info(g.db, id)

    return render_template("movie/detail.html", movie = current_movie)

@blueprint.route("/recent25")
def recent25():
    return "最近25部电影"

@blueprint.route("/classification")
def classification():
    return "电影分类"