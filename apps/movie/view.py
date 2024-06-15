from flask import Blueprint, render_template, g
from extensions import Movie

blueprint = Blueprint("movie", __name__)

@blueprint.route("/top25")
def top25():
    movie = Movie()
    movies = movie.top(g.db, 25)

    print(movies)

    return render_template("movie/top.html", movies_info = movies)