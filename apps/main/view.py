from flask import Blueprint, render_template
from extensions import Movie

blueprint = Blueprint("main", __name__)

@blueprint.route("/")
def index():
    return render_template("/main/index.html")