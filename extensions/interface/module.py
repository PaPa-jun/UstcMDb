class User:
    """
    用户接口
    """
    def __init__(self, id) -> None:
        self.id = id

    def get_info(self, db):
        with db.cursor() as cursor:
            cursor.execute('SELECT username, avatar, email, bio, birthday FROM user WHERE id=%s', (self.id))
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
                with db.cursor() as cursor:
                    cursor.execute("SELECT name FROM worker WHERE id=%s", (worker['worker_id'],))
                    name = cursor.fetchone()['name']
                movie_info['director'].append(name)
            if worker['job'] == 'actor':
                with db.cursor() as cursor:
                    cursor.execute("SELECT name FROM worker WHERE id=%s", (worker['worker_id'],))
                    name = cursor.fetchone()['name']
                movie_info['casts'].append(name)

        return movie_info

    def top(self, db, range):
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM movie ORDER BY rating DESC LIMIT %s", (range,))
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