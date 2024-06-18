from flask import Blueprint, render_template, g, request, flash, redirect, url_for, jsonify
from extensions import Movie, Cast, Review, User, Genres
from datetime import datetime
import uuid


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
    genres = Genres()
    year_and_movies = genres.by_decade(g.db)
    print(year_and_movies)
    return render_template("movie/classification.html", movies = year_and_movies)

@blueprint.route("/<id>")
def movie_detail(id):
    movie = Movie()
    current_movie = movie.get_info(g.db, id)
    worker = Cast()
    workers = []
    
    for director in current_movie['director']:
        director_name = director['name']
        worker_id = worker.get_id_by_name(director_name, g.db)
        worker_info = worker.get_info(worker_id, g.db)
        workers.append({
            'name': director_name,
            'imdbID' : director['imdbID'],
            'avatar': worker_info['avatar'].split(',')[0] if worker_info['avatar'] else None,
            'photo_set': worker_info['avatar'],
            'bio': worker_info['bio'],
            'birth': worker_info['birth'],
            'other_work': worker_info['job'],
            'role': None,
            'this_work': 'director'
        })
    
    for cast in current_movie['casts']:
        cast_name = cast['name']
        worker_id = worker.get_id_by_name(cast_name, g.db)
        worker_info = worker.get_info(worker_id, g.db)
        workers.append({
            'name': cast_name,
            'imdbID' : cast['imdbID'],
            'avatar': worker_info['avatar'].split(',')[0] if worker_info['avatar'] else None,
            'photo_set': worker_info['avatar'],
            'bio': worker_info['bio'],
            'birth': worker_info['birth'],
            'other_work': worker_info['job'],
            'role': worker.get_role(worker_id, current_movie['id'], g.db),
            'this_work': 'actor'
        })

    review_scraper = Review()
    reviews = review_scraper.get_review(id, g.db)
    for review in reviews:
        user = User(review['writer_id'])
        user.get_info(g.db)
        review['writer_info'] = user.return_info()
    return render_template("movie/detail.html", movie=current_movie, workers=workers, reviews=reviews)

@blueprint.route("/<id>", methods=['GET', 'POST'])
def rating(id):
    if request.method == 'POST':
        rating = request.form['rating']
        with g.db.cursor() as cursor:
            query = """
            SELECT rating FROM user_movie_rating WHERE user_id=%s AND movie_id=%s;
            """
            cursor.execute(query, (g.current_user['id'], id))
            rating = cursor.fetchone()
        
        if not rating:
            with g.db.cursor() as cursor:
                query = """
                INSERT INTO user_movie_rating (user_id, movie_id, rating)
                VALUES (%s, %s, %s);
                """
                cursor.execute(query, (g.current_user['id'], id, rating))
            g.db.commit()
            with g.db.cursor() as cursor:
                query = """
                SELECT AVG(rating) FROM user_movie_rating WHERE movie_id=%s;
                """
                cursor.execute(query, (id,))
                rating_avg = cursor.fetchone()
                query = """
                UPDATE movie SET local_rating=%s WHERE id=%s;
                """
                cursor.execute(query, (rating_avg['AVG(rating)'], id))
            g.db.commit()
        else:
            flash("您已评过分。")
    return redirect(url_for('movie.movie_detail', id=id))

@blueprint.route('/add_comment', methods=['POST'])
def add_comment():
    data = request.get_json()
    movie_id = data.get('movie_id')
    comment_text = data.get('comment')
    comment_date = data.get('comment_date')
    
    if not movie_id or not comment_text or not comment_date:
        return jsonify({'error': '缺少必要的评论信息'}), 400
    
    # 将ISO 8601日期格式转换为YYYY-MM-DD HH:MM:SS
    comment_date = datetime.strptime(comment_date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
    
    with g.db.cursor() as cursor:
        query = """
        INSERT INTO review (id, movie_id, writer_id, content, date)
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(query, ('rev_' + str(uuid.uuid4())[:10], movie_id, g.current_user['id'], comment_text, comment_date))
    g.db.commit()
    response = {'message': '评论已成功提交', 'comment': comment_text, 'movie_id': movie_id, 'comment_date': comment_date}

    return jsonify(response)

@blueprint.route('/delete_comment', methods=['POST'])
def delete_comment():
    comment_id = request.form.get('comment_id')
    movie_id = request.form.get('movie_id')
    
    if not comment_id:
        print(request.form.get('comment_date'))
        return redirect(url_for('movie.movie_detail', id=movie_id))

    with g.db.cursor() as cursor:
        cursor.execute("DELETE FROM review WHERE id=%s", (comment_id,))
    g.db.commit()
    flash("评论已删除。")
    return redirect(url_for('movie.movie_detail', id=movie_id))

@blueprint.route('/like', methods=['POST'])
def like_review():
    data = request.get_json()
    review_id = data.get('review_id')

    return review_id

    # return jsonify({'success': True, 'likes': review.likes})
