from imdb import Cinemagoer
from googleapiclient.discovery import build
from tqdm import tqdm
import json, pymysql, uuid

class IMDb:
    """
    爬取电影信息
    """

    def __init__(self) -> None:
        self.ia = Cinemagoer()
        self.youtube_api_key = 'AIzaSyDVuoeGmXOgitKNWmJlnSFoFjPMShLN9dQ'
        self.youtube_service = build('youtube', 'v3', developerKey=self.youtube_api_key)

    def fetch_movie_info(self, movie):
        movie_id = movie.movieID
        try:
            movie_info = self.ia.get_movie(movie_id, info=['main', 'plot', 'full credits'])

            # 获取预告片信息
            trailer_url = self.get_trailer_url(movie_info.get('title'))

            movie_details = {
                'id': 'mov_' + str(uuid.uuid4())[:10],
                'title': movie_info.get('title'),
                'year': movie_info.get('year'),
                'rating': movie_info.get('rating'),
                'directors': [{'id': 'cas_' + str(uuid.uuid4())[:10], 'name': director['name']} for director in movie_info.get('directors', [])],
                'cast': [{'id': 'cas_' + str(uuid.uuid4())[:10], 'name': actor['name']} for actor in movie_info.get('cast', [])[:10]],  # 只获取前10个演员
                'genres': ", ".join(movie_info.get('genres', [])),  # 将 genres 列表转换为逗号分隔的字符串
                'plot': movie_info.get('plot outline'),
                'poster': movie_info.get('full-size cover url'),
                'duration': movie_info.get('runtime'),
                'trailer': trailer_url
            }
        except Exception as e:
            print(f"Error fetching info for movie {movie}: {e}")
            return None
        
        return movie_details
    
    def search_movie(self, movie):
        search_results = self.ia.search_movie(movie)
        if not search_results:
            return None
        
        return self.fetch_movie_info(search_results[0])
    
    def fetch_top_250_movies(self):
        movies_info = []
        movies = self.ia.get_top250_movies()
        for movie in tqdm(movies, desc="Fetching movie info"):
            movie_info = self.fetch_movie_info(movie)
            if movie_info:
                movies_info.append(movie_info)
        
        return movies_info
        
    def to_json(self, movies, save_path):
        with open(save_path, 'w', encoding='utf-8') as file:
            json.dump(movies, file, ensure_ascii=False, indent=4)

    def get_trailer_url(self, movie_title):
        try:
            request = self.youtube_service.search().list(
                q=f"{movie_title} trailer",
                part='snippet',
                type='video',
                maxResults=1
            )
            response = request.execute()
            if response['items']:
                trailer_url = f"https://www.youtube.com/embed/{response['items'][0]['id']['videoId']}"
                return trailer_url
        except Exception as e:
            print(f"Error fetching trailer for movie {movie_title}: {e}")
        return None
    
    def search_person(self, name):
        search_results = self.ia.search_person(name)
        if not search_results:
            return None
        
        return self.fetch_person_info(search_results[0])
    
    def fetch_person_info(self, person):
        person_id = person.personID
        try:
            person_info = self.ia.get_person(person_id)
            gender = person_info.get('gender')
            birth_date = person_info.get('birth date')
            bio = " ".join(person_info.get('mini biography', [])) if 'mini biography' in person_info else None
            other_works = " ".join(person_info.get('other works', [])) if 'other works' in person_info else None
            job = other_works if other_works else None
            person_details = {
                'id': 'wrk_' + str(uuid.uuid4())[:10],
                'name': person_info.get('name'),
                'birth': birth_date,
                'avatar': person_info.get('headshot'),
                'gender': gender[0].upper() if gender else None,
                'job': job,
                'bio': bio
            }
        except Exception as e:
            print(f"Error fetching info for person {person}: {e}")
            return None
        
        return person_details

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
            database=self.database,
            charset=self.charset,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    
    def load_json_into_db(self, json_file, connection):
        with open(json_file, 'r', encoding='utf-8') as file:
            movies = json.load(file)
        
        try:
            with connection.cursor() as cursor:
                for movie in movies:
                    # 插入电影信息
                    sql_movie = """
                    INSERT INTO movie (id, title, year, duration, rating, plot, poster, trailer, genres)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        title = VALUES(title),
                        year = VALUES(year),
                        duration = VALUES(duration),
                        rating = VALUES(rating),
                        plot = VALUES(plot),
                        poster = VALUES(poster),
                        trailer = VALUES(trailer),
                        genres = VALUES(genres);
                    """
                    cursor.execute(sql_movie, (movie['id'], movie['title'], movie['year'], movie['duration'], movie['rating'], movie['plot'], movie['poster'], movie['trailer'], movie['genres']))
                    
                    # 插入导演信息并建立关系
                    for director in movie['directors']:
                        sql_worker = """
                        INSERT INTO worker (id, name, job)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            name = VALUES(name),
                            job = VALUES(job);
                        """
                        cursor.execute(sql_worker, (director['id'], director['name'], 'director'))
                        
                        sql_movie_worker = """
                        INSERT INTO movie_worker (movie_id, worker_id, job)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            job = VALUES(job);
                        """
                        cursor.execute(sql_movie_worker, (movie['id'], director['id'], 'director'))
                    
                    # 插入演员信息并建立关系
                    for actor in movie['cast']:
                        sql_worker = """
                        INSERT INTO worker (id, name, job)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            name = VALUES(name),
                            job = VALUES(job);
                        """
                        cursor.execute(sql_worker, (actor['id'], actor['name'], 'actor'))
                        
                        sql_movie_worker = """
                        INSERT INTO movie_worker (movie_id, worker_id, job)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            job = VALUES(job);
                        """
                        cursor.execute(sql_movie_worker, (movie['id'], actor['id'], 'actor'))
                
                connection.commit()
        except Exception as e:
            print(f"Error inserting data into the database: {e}")
            connection.rollback()
        finally:
            connection.close()

class Scraper:
    """
    爬虫
    """

    