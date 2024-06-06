from flask import Blueprint

blueprint = Blueprint("movie", __name__)

@blueprint.route("/top25")
def top25():
    return "top 25 movies."