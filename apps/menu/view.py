from flask import Blueprint, render_template

blueprint = Blueprint("menu", __name__)

@blueprint.route("/")
def index():
    return render_template("/menu/index.html")