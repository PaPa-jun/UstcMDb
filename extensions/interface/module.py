class User:
    """
    用户接口
    """
    def __init__(self, id) -> None:
        self.id = id

    def get_info(self, db):
        with db.cursor() as cursor:
            cursor.execute('SELECT username, avatar, email, bio, birthday FROM user WHERE id=%s', (self.id,))
            current_user = cursor.fetchone()

        self.username = current_user['username']
        self.avatar = current_user['avatar']
        self.email = current_user['email']
        self.bio = current_user['bio']
        self.birthday = current_user['birthday']

    def update_info(self, db, item_name, content):
        if item_name not in ['username', 'avatar', 'email', 'bio', 'birthday']:
            raise ValueError("Invalid item name")

        query = f"UPDATE user SET {item_name} = %s WHERE id = %s"

        with db.cursor() as cursor:
            cursor.execute(query, (content, self.id))
            db.commit()

class Movie:
    """
    电影接口
    """
    def __init__(self) -> None:
        pass
    
    def get_info(self, db, id):
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM movie WHERE id=%s", (id,))
            movie_info = cursor.fetchone()
            cursor.execute("SELECT * FROM movie_worker WHERE movie_id=%s", (id,))
            movie_workers = cursor.fetchall()
            movie_info['director'] = []
            movie_info['casts'] = []
            for worker in movie_workers:
                if worker['job'] == 'director':
                    cursor.execute("SELECT name, imdbID FROM worker WHERE id=%s", (worker['worker_id'],))
                    info = cursor.fetchone()
                    name = info['name']
                    imdbID = info['imdbID']
                    movie_info['director'].append({'name':name, 'imdbID':imdbID})
                if worker['job'] == 'actor':
                    cursor.execute("SELECT name, imdbID FROM worker WHERE id=%s", (worker['worker_id'],))
                    info = cursor.fetchone()
                    name = info['name']
                    imdbID = info['imdbID']
                    movie_info['casts'].append({'name':name, 'imdbID':imdbID})
        return movie_info

    def top(self, db, range):
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM movie ORDER BY imdb_rating DESC, local_rating DESC LIMIT %s", (range,))
            movies = cursor.fetchall()  # fetchall instead of fetchone to get multiple records
            
        movies_info = []
        for movie in movies:
            movies_info.append(self.get_info(db, movie['id']))
        return movies_info
    
    def recent(self, db, range):
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM movie ORDER BY year DESC LIMIT %s", (range,))
            movies = cursor.fetchall()  # fetchall instead of fetchone to get multiple records
            
        movies_info = []
        for movie in movies:
            movies_info.append(self.get_info(db, movie['id']))
        return movies_info
    
    def random_movie(self, db, range):
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM movie ORDER BY RAND(%s) LIMIT %s", (42,range,))
            movies = cursor.fetchall()  # fetchall instead of fetchone to get multiple records
            
        movies_info = []
        for movie in movies:
            movies_info.append(self.get_info(db, movie['id']))
        return movies_info
    
class Cast:
    """
    演职人员接口
    """

    def __init__(self) -> None:
        pass

    def get_info(self, id, db):
        with db.cursor() as cursor:
            cursor.execute('SELECT * FROM worker WHERE id=%s', (id,))
            worker_info = cursor.fetchone()
            cursor.execute('SELECT movie_id FROM movie_worker WHERE worker_id=%s', (id,))
            attended_movies = cursor.fetchall()
            worker_info['movies'] = []
            for movie in attended_movies:
                for value in movie.values():
                    cursor.execute("SELECT title FROM movie WHERE id=%s", (value,))
                    movie_title = cursor.fetchone()
                    worker_info['movies'].append(movie_title['title'] if movie_title else None)
        return worker_info

    def get_id_by_name(self, name, db):
        with db.cursor() as cursor:
            cursor.execute('SELECT id FROM worker WHERE name=%s', (name,))
            name = cursor.fetchone()
        return name['id']
    
    def get_role(self, worker_id, movie_id, db):
        with db.cursor() as cursor:
            cursor.execute('SELECT role FROM movie_worker WHERE movie_id=%s AND worker_id=%s', (movie_id, worker_id))
            roles_list = cursor.fetchall()
        roles = []
        for roles_dic in roles_list:
            if roles_dic:
                roles.append(roles_dic['role'])
        return roles
    
class Review:
    """
    评论接口
    """

    def __init__(self) -> None:
        pass