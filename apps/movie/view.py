from flask import Blueprint, render_template, g
from extensions import Movie, Cast

blueprint = Blueprint("movie", __name__)

@blueprint.route("/top25")
def top25():
    movie = Movie()
    movies = movie.top(g.db, 25)
    return render_template("movie/top.html", movies_info = movies)

@blueprint.route("/recent25")
def recent25():
    movie = Movie()
    movies = movie.recent(g.db, 25)
    return render_template("movie/recent.html", movies = movies)

@blueprint.route("/classification")
def classification():
    return "电影分类"


@blueprint.route("/<id>")
def movie_detail(id):
    movie = Movie()
    current_movie = movie.get_info(g.db, id)
    worker = Cast()
    workers = []
    
    for director in current_movie['director']:
        worker_id = worker.get_id_by_name(director, g.db)
        worker_info = worker.get_info(worker_id, g.db)
        workers.append({
            'name': director,
            'avatar': worker_info['avatar'].split(',')[0] if worker_info['avatar'] else None,
            'photo_set': worker_info['avatar'],
            'bio': worker_info['bio'],
            'birth': worker_info['birth'],
            'other_work': worker_info['job'],
            'role': None,
            'this_work': 'director'
        })
    
    for cast in current_movie['casts']:
        worker_id = worker.get_id_by_name(cast, g.db)
        worker_info = worker.get_info(worker_id, g.db)
        workers.append({
            'name': cast,
            'avatar': worker_info['avatar'].split(',')[0] if worker_info['avatar'] else None,
            'photo_set': worker_info['avatar'],
            'bio': worker_info['bio'],
            'birth': worker_info['birth'],
            'other_work': worker_info['job'],
            'role': worker.get_role(worker_id, current_movie['id'], g.db),
            'this_work': 'actor'
        })

    return render_template("movie/detail.html", movie=current_movie, workers=workers)
