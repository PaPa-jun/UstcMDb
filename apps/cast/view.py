from flask import Blueprint,render_template, g
from extensions import Cast

blueprint = Blueprint("cast", __name__)

@blueprint.route('/<id>')
def cast_profile(id):
    cast = Cast()
    cast_info = cast.get_info(id, g.db)
    return render_template("casts/detail.html", cast = cast_info)