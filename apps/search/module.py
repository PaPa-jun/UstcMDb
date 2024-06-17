from extensions import Cast, Movie

class Search:
    """
    搜索模块
    """

    def __init__(self, search_type, keywords, db) -> None:
        self.type = search_type
        self.keywords = keywords
        self.db = db
        self.results = []

    def search(self):
        if self.type == "movies":
            self.search_movie()
        elif self.type == "actors":
            self.search_actor()

    def search_movie(self):
        with self.db.cursor() as cursor:
            sql = "SELECT id FROM movie WHERE title LIKE %s ORDER BY local_rating DESC, imdb_rating DESC"
            cursor.execute(sql, ('%' + self.keywords + '%',))
            ids = cursor.fetchall()
        movie = Movie()
        self.results = []
        for id in ids:
            result = movie.get_info(id = id['id'], db = self.db)
            self.results.append(result)

    def search_actor(self):
        with self.db.cursor() as cursor:
            sql = "SELECT id FROM worker WHERE name LIKE %s"
            cursor.execute(sql, ('%' + self.keywords + '%',))
            ids = cursor.fetchall()
        
        cast = Cast()
        self.results = []
        for id in ids:
            result = cast.get_info(id = id['id'], db = self.db)
            self.results.append(result)
        self.results.sort(key=lambda x: len(x['movies']), reverse=True)