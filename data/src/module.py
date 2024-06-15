from imdb import Cinemagoer
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime
import json, pymysql, uuid, requests

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
            scraper = PersonScraper(person_id)
            person_details = {
                'birth': scraper.get_birth_date(),
                'avatar': scraper.get_avatar_url()['srcset'],
                'job': scraper.get_other_works(),
                'bio': scraper.get_bio()
            }
        except Exception as e:
            print(f"Error fetching info for person {person}: {e}")
            return None
        
        return person_details
    
    def fetch_all_casts_info_from_db(self, db):
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT name FROM worker;")
                worker_names = cursor.fetchall()

            # 添加进度条
            for worker in tqdm(worker_names, desc="Fetching and updating worker info"):
                worker_info = self.search_person(worker['name'])
                if worker_info:
                    query = """
                    UPDATE worker
                    SET avatar = %s,
                        birth = %s,
                        job = %s,
                        bio = %s
                    WHERE name = %s;
                    """
                    with db.cursor() as cursor:
                        cursor.execute(query, (worker_info['avatar'], worker_info['birth'], worker_info['job'], worker_info['bio'], worker['name']))
            
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error fetching and updating worker info: {e}")

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
    
    def load_movie_from_json(self, json_file, connection):
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
                        INSERT INTO worker (id, name)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE
                            name = VALUES(name);
                        """
                        cursor.execute(sql_worker, (director['id'], director['name']))
                        
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
                        INSERT INTO worker (id, name)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE
                            name = VALUES(name);
                        """
                        cursor.execute(sql_worker, (actor['id'], actor['name']))
                        
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

    def update_casts_from_json(self):
        pass

class PersonScraper:
    """
    爬虫
    """

    def __init__(self, id) -> None:
        self.url = "https://www.imdb.com/name/nm" + id + "/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1',
        }
        self.response = requests.get(self.url, headers=self.headers)
        if self.response.status_code == 200:
            self.html = self.response.content
            self.soup = BeautifulSoup(self.html, 'html.parser')
        else:
            print(f"Failed to retrieve content: {self.response.status_code}")
            self.soup = None

    def get_name(self):
        if self.soup:
            name_tag = self.soup.find('span', {'class': 'hero__primary-text', 'data-testid': 'hero__primary-text'})
            if name_tag:
                return name_tag.text.strip()
        return None
    
    def get_avatar_url(self):
        if self.soup:
            image_tag = self.soup.find('img', {'class': 'ipc-image'})
            if image_tag:
                image_src = image_tag.get('src')
                image_srcset = image_tag.get('srcset')
                return {
                    'src': image_src,
                    'srcset': image_srcset
                }
        return None
    
    def get_birth_date(self):
        if self.soup:
            birth_date_tag = self.soup.find('li', {'role': 'presentation', 'class': 'ipc-inline-list__item test-class-react'})
            if birth_date_tag:
                month_day = birth_date_tag.find_all('a')[0].text.strip()
                year = birth_date_tag.find_all('a')[1].text.strip()
                birth_date_str = f"{month_day}, {year}"
                birth_date = datetime.strptime(birth_date_str, "%B %d, %Y").date()
                return birth_date
        return None
    
    def get_other_works(self):
        if self.soup:
            other_works_tag = self.soup.find('li', {'role': 'presentation', 'class': 'ipc-metadata-list__item ipc-metadata-list-item--link', 'data-testid': 'nm_pd_wrk'})
            if other_works_tag:
                other_works_div = other_works_tag.find('div', {'class': 'ipc-html-content-inner-div'})
                if other_works_div:
                    return other_works_div.text.strip()
        return None
    
    def get_bio(self):
        if self.soup:
            bio_tag = self.soup.find('div', {'class': 'ipc-overflowText--children'})
            if bio_tag:
                bio_div = bio_tag.find('div', {'class': 'ipc-html-content-inner-div'})
                if bio_div:
                    return bio_div.text.strip()
        return None
