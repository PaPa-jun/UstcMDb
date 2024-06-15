from flask import Blueprint

blueprint = Blueprint("movie", __name__)

@blueprint.route("/top25")
def top25():
    return "top 25 movies."

@blueprint.route("/recent25")
def recent25():
    return "最新25"

@blueprint.route("/classification")
def classification():
    return "电影分类"
