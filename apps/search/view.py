from flask import Blueprint, request, render_template, flash, g
from apps.search.module import Search

blueprint = Blueprint("search", __name__)

@blueprint.route('/')
def search():
    search_type = request.args.get('type')
    keyword = request.args.get('keyword')
    search = Search(search_type, keyword, g.db)
    search.search()

    if not search.results:
        flash('No results found!')

    return render_template('search/results.html', results=search.results, keyword=keyword, search_type=search_type)