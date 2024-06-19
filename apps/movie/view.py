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
    
    comment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
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
        try:
            # 删除与该评论相关的所有子评论（如果有）
            cursor.execute("DELETE FROM review WHERE review_id=%s", (comment_id,))
            # 最后删除评论
            cursor.execute("DELETE FROM review WHERE id=%s", (comment_id,))
            g.db.commit()
        except Exception as e:
            g.db.rollback()
            flash("删除评论失败: {}".format(str(e)))
            return redirect(url_for('movie.movie_detail', id=movie_id))

    flash("评论已删除。")
    return redirect(url_for('movie.movie_detail', id=movie_id))


@blueprint.route('/like_review', methods=['POST'])
def like_review():
    data = request.get_json()
    review_id = data.get('review_id')
    
    # 获取当前的点赞数
    with g.db.cursor() as cursor:
        cursor.execute("SELECT likes FROM review WHERE id=%s", (review_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'success': False, 'message': '评论不存在'})
        current_likes = result['likes']
    
    # 更新点赞数
    new_likes = current_likes + 1
    with g.db.cursor() as cursor:
        cursor.execute("UPDATE review SET likes=%s WHERE id=%s", (new_likes, review_id))
    g.db.commit()
    
    return jsonify({'success': True, 'likes': new_likes})


@blueprint.route('/reply', methods=['POST'])
def reply_comment():
    data = request.get_json()
    with g.db.cursor() as cursor:
        query = """
        INSERT INTO review (id, movie_id, writer_id, user_id, content, review_id, date)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(query, ('rev_' + str(uuid.uuid4())[:10], data.get('movie_id'), data.get('writer_id'), data.get('user_id'), data.get('content'), data.get('review_id'), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    g.db.commit()

    return jsonify({"status" : "success"}), 200