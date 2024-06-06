from imdb import Cinemagoer
from tqdm import tqdm
import json, pymysql

class IMDb:
    """
    爬取电影信息
    """

    def __init__(self) -> None:
        self.ia = Cinemagoer()

    def fetch_movie_info(self, movie):
        movie_id = movie.movieID
        movie_info = self.ia.get_movie(movie_id)
        
        movie_details = {
            'title': movie_info.get('title'),
            'year': movie_info.get('year'),
            'rating': movie_info.get('rating'),
            'directors': [director['name'] for director in movie_info.get('directors', [])],
            'cast': [actor['name'] for actor in movie_info.get('cast', [])[:10]],  # 只获取前10个演员
            'genres': movie_info.get('genres'),
            'plot': movie_info.get('plot outline')
        }
        
        return movie_details
    
    def search_movie(self, movie):
        search_results = self.ia.search_movie(movie)
        if not search_results:
            return None
        
        return self.fetch_movie_info(movie=search_results[0])
    
    def fetch_top_250_movies(self):
        movies_info = []
        movies = self.ia.get_top250_movies()
        for movie in tqdm(movies, desc="Fetching movie info"):
            try:
                movie_info = self.fetch_movie_info(movie)
                if movie_info:
                    movies_info.append(movie_info)
            except Exception as e:
                print(f"Error fetching info for movie {movie}: {e}")
        
        return movies_info
        
    def to_json(self, movies, save_path):
        with open(save_path, 'w', encoding='utf-8') as file:
            json.dump(movies, file, ensure_ascii=False, indent=4)

class DataBase:
    """
    数据库
    """

    def __init__(self, host, password, database, port=3306, user='root', charset='utf8mb4') -> None:
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.database = database
        self.charset = charset

    def connect_db(self):
        connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.schema,
            charset=self.charset,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    
    def load_json_into_db(self, json_file, table, connection):
        pass

class User:
    """
    用户
    """

    def __init__(self):
        pass