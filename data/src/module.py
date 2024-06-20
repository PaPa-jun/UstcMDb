from imdb import Cinemagoer
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime
from faker import Faker
from werkzeug.security import generate_password_hash
import json, pymysql, uuid, requests

GOOGLE_YOUTUBE_API_KEY = "Your API Key"

class IMDb:
    """
    访问 IMDb 数据
    """
    def __init__(self) -> None:
        self.ia = Cinemagoer()
        self.youtube_api_key = GOOGLE_YOUTUBE_API_KEY
        self.youtube_service = build('youtube', 'v3', developerKey=self.youtube_api_key)

class HtmlScraper(IMDb):
    """
    利用 HTML 抓取网页信息
    """

    def __init__(self) -> None:
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1',
        }
        self.url_map = {
            "cast": "https://www.imdb.com/name/{}/",
            "review": "https://www.imdb.com/title/{}/reviews/"
        }

    def get_response(self, url_key, id):
        url = self.url_map[url_key].format(id)
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            self.html = response.content
            self.soup = BeautifulSoup(self.html, 'html.parser')
        else:
            print(f"Failed to retrieve content: {response.status_code} for url: {url}")
            self.soup = None

class MovieScraper(HtmlScraper):
    """
    获取电影信息
    """

    def get_trailer_url(self, movie_title):
        """
        获取预告片链接
        """
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

    def fetch_movie_info(self, movie_id):
        """
        获取电影信息
        """
        movie_info = self.ia.get_movie(movie_id, info=['main', 'plot', 'full credits'])
        trailer_url = self.get_trailer_url(movie_info.get('title'))

        movie_details = {
            'id': 'mov_' + str(uuid.uuid4())[:10],
            'title': movie_info.get('title'),
            'year': movie_info.get('year'),
            'imdb_rating': movie_info.get('rating'),
            'directors': [
                {
                    'id': None, 
                    'name': director['name'], 
                    'imdbID': f"nm{director.personID}"
                } for director in movie_info.get('directors', [])
            ],
            'casts': [
                {
                    'id': None,
                    'name': actor['name'],
                    'character': str(actor.currentRole) if actor.currentRole else None,
                    'imdbID': f"nm{actor.personID}"
                } for actor in movie_info.get('cast', [])[:10]
            ],
            'genres': ", ".join(movie_info.get('genres', [])),
            'plot': movie_info.get('plot outline'),
            'poster': movie_info.get('full-size cover url'),
            'duration': movie_info.get('runtime'),
            'trailer': trailer_url,
            'imdbID': f"tt{movie_id}"
        }
        
        return movie_details

    def gen_id(self, movies):
        visited = {}
        for movie in movies:
            for director in movie['directors']:
                if director['imdbID'] not in visited or director['imdbID'] is None:
                    director['id'] = 'cas_' + str(uuid.uuid4())[:10]
                    visited[director['imdbID']] = director['id']
                else:
                    director['id'] = visited[director['imdbID']]
            for cast in movie['casts']:
                if cast['imdbID'] not in visited or cast['imdbID'] is None:
                    cast['id'] = 'cas_' + str(uuid.uuid4())[:10]
                    visited[cast['imdbID']] = cast['id']
                else:
                    cast['id'] = visited[cast['imdbID']]
    
    def search_movie_by_name(self, movie):
        """
        依据电影名称搜索电影信息
        """
        search_results = self.ia.search_movie(movie)
        if not search_results:
            return None
        
        return self.fetch_movie_info(search_results[0].movieID)
    
    def fetch_top_25_movies(self):
        """
        抓取 IMDb Top 25 的电影信息
        """
        movies_info = []
        movies = self.ia.get_top250_movies()
        for movie in tqdm(movies, desc="Fetching movie info"):
            movie_info = self.fetch_movie_info(movie.movieID)
            if movie_info:
                movies_info.append(movie_info)
        
        return movies_info
    
    def fetch_bottom_25_movies(self):
        """
        抓取 IMDb Bottom 25 的电影信息
        """
        movies_info = []
        movies = self.ia.get_bottom100_movies()
        for movie in tqdm(movies, desc="Fetching movie info"):
            movie_info = self.fetch_movie_info(movie.movieID)
            if movie_info:
                movies_info.append(movie_info)
        return movies_info
    
    def fetch_popular_25_movies(self):
        """
        抓取 IMDb Popular 25 的电影信息
        """
        movies_info = []
        movies = self.ia.get_popular100_movies()
        for movie in tqdm(movies, desc="Fetching movie info"):
            movie_info = self.fetch_movie_info(movie.movieID)
            if movie_info:
                movies_info.append(movie_info)
        return movies_info
    
    def fetch_india_movies(self):
        """
        抓取印度电影
        """
        movies_info = []
        movies = self.ia.get_top250_indian_movies()
        for movie in tqdm(movies, desc="Fetching movie info"):
            movie_info = self.fetch_movie_info(movie.movieID)
            if movie_info:
                movies_info.append(movie_info)
        return movies_info

class CastScraper(HtmlScraper):
    """
    获取演职人员信息
    """

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
                links = birth_date_tag.find_all('a')
                if len(links) >= 2:
                    month_day = links[0].text.strip()
                    year = links[1].text.strip()
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
    
    def fetch_cast_info(self, person_id):
        self.get_response("cast", person_id)
        person_details = {
            'birth': self.get_birth_date().strftime("%Y-%m-%d") if self.get_birth_date() else None,
            'avatar' : self.get_avatar_url()['src'] if self.get_avatar_url()['src'] else None,
            'srcset': self.get_avatar_url()['srcset'] if self.get_avatar_url()['srcset'] else None,
            'job': self.get_other_works() if self.get_other_works() else None,
            'bio': self.get_bio() if self.get_bio() else None,
            'imdbID' : f"{person_id}"
        }
        
        return person_details
    
    def fetch_all_casts_info_from_db(self, db):
        with db.cursor() as cursor:
            cursor.execute("SELECT id, name, imdbID FROM worker;")
            worker_names = cursor.fetchall()

        workers_info = []
        for worker in tqdm(worker_names, desc="Fetching and updating worker info"):
            info = self.fetch_cast_info(worker['imdbID'])
            worker_info = info if info else {}
            worker_info['id'] = worker['id']
            worker_info['name'] = worker['name']
            workers_info.append(worker_info)
        
        return workers_info
    
    def search_cast(self, name):
        """
        访问 IMDb 搜索个人信息
        """
        search_results = self.ia.search_person(name)
        if not search_results:
            return None
        return self.fetch_cast_info(search_results[0].personID)
    
class ReviewScraper(HtmlScraper):
    """
    评论信息获取
    """

    def get_reviews(self, id):
        self.get_response("review", id)
        reviews = []
        if self.soup:
            review_containers = self.soup.find_all('div', class_='lister-item-content')
            for container in review_containers:
                title_tag = container.find('a', class_='title')
                title = title_tag.text.strip() if title_tag else None

                rating_tag = container.find('span', class_='rating-other-user-rating')
                rating = rating_tag.find('span').text.strip() if rating_tag else None
                if rating: rating = 9.9 if float(rating) > 9.9 else float(rating)

                text_tag = container.find('div', class_='text')
                text = text_tag.text.strip() if text_tag else None

                date_tag = container.find('span', class_='review-date')
                date = date_tag.text.strip() if date_tag else None
                try:
                    date = datetime.strptime(date, '%d %B %Y').strftime('%Y-%m-%d')
                except ValueError:
                    date = None

                author_tag = container.find('span', class_='display-name-link')
                author = author_tag.text.strip() if author_tag else None

                reviews.append({
                    'title': title,
                    'rating': rating,
                    'text': text,
                    'date': date,
                    'author': author
                })
        return reviews
    
    def fetch_all_reviews(self, db):
        all_reviews = {}
        imdb = IMDb()
        with db.cursor() as cursor:
            cursor.execute("SELECT title, imdbID FROM movie;")
            movies = cursor.fetchall()

        for movie in tqdm(movies, desc="Fetching reviews"):
            movie_title = movie['title']
            movie_id = movie['imdbID']
            reviews = self.get_reviews(movie_id)
            all_reviews[movie_title] = reviews
        
        return all_reviews
    
class Scraper:
    """
    爬虫
    """

    def __init__(self) -> None:
        self.movie_scraper = MovieScraper()
        self.cast_scraper = CastScraper()
        self.review_scraper = ReviewScraper()
        
    def to_json(self, data, save_path: str) -> None:
        """
        将传入的列表或字典生成 JSON 文件并保存到指定路径。

        :param data: 要转换为 JSON 的数据，可以是列表或字典
        :param save_path: 保存 JSON 文件的路径
        """
        with open(save_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"JSON 文件已保存到 {save_path}")

class User:
    """
    生成用户
    """

    def __init__(self) -> None:
        self.fake = Faker()
    
    def gen_fake_user(self, username, email, id=None):
        user = {
            'id': id if id else 'usr_' + str(uuid.uuid4())[:10],
            'avatar': "images/avatars/fixed_pics/default.jpg",
            'username': username,
            'password': generate_password_hash(self.fake.password()),
            'email': email,
            'bio': "I'm a fake user.",
            'birthday': self.fake.date_of_birth().strftime('%Y-%m-%d')
        }
        return user
    
    def create_user_from_reviews(self, reviews):
        users = []
        usernames = set()
        emails = set()

        with open(reviews, 'r', encoding='utf-8') as file:
            movies = json.load(file)

        for movie_reviews in tqdm(movies.values(), desc="Creating users"):
            for review in movie_reviews:
                username = review['author']
                if not username:
                    username = self.fake.user_name()
                    usernames.add(username)
                if username in usernames:
                    continue

                email = self.fake.email()
                while email in emails:
                    email = self.fake.email()
                emails.add(email)

                user = self.gen_fake_user(username=username, email=email)
                users.append(user)
        
        return users
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
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset,
            cursorclass=pymysql.cursors.DictCursor
        )
    
    def load_movie_from_json(self, json_file):
        with open(json_file, 'r', encoding='utf-8') as file:
            movies = json.load(file)
        
        with self.connection.cursor() as cursor:
            for movie in tqdm(movies, desc="Inserting Movies: "):
                # 插入电影信息
                sql_movie = """
                INSERT INTO movie (id, title, year, duration, imdb_rating, local_rating, plot, poster, trailer, genres, imdbID)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    year = VALUES(year),
                    duration = VALUES(duration),
                    imdb_rating = VALUES(imdb_rating),
                    local_rating = VALUES(local_rating),
                    plot = VALUES(plot),
                    poster = VALUES(poster),
                    trailer = VALUES(trailer),
                    genres = VALUES(genres);
                """
                cursor.execute(sql_movie, (movie['id'], movie['title'], movie['year'], movie['duration'], movie['imdb_rating'], 0, movie['plot'], movie['poster'], movie['trailer'], movie['genres'], movie['imdbID']))

                # 插入导演信息并建立关系
                for director in movie['directors']:
                    sql_worker = """
                    INSERT INTO worker (id, name, imdbID)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        name = VALUES(name);
                    """
                    cursor.execute(sql_worker, (director['id'], director['name'], director['imdbID']))

                    sql_movie_worker = """
                    INSERT INTO movie_worker (movie_id, worker_id, job, role)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        job = VALUES(job);
                    """
                    cursor.execute(sql_movie_worker, (movie['id'], director['id'], 'director', None))

                # 插入演员信息并建立关系
                for actor in movie['casts']:
                    sql_worker = """
                    INSERT INTO worker (id, name, imdbID)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        name = VALUES(name);
                    """
                    cursor.execute(sql_worker, (actor['id'], actor['name'], actor['imdbID']))

                    sql_movie_worker = """
                    INSERT INTO movie_worker (movie_id, worker_id, job, role)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        job = VALUES(job),
                        role = VALUES(role);
                    """
                    cursor.execute(sql_movie_worker, (movie['id'], actor['id'], 'actor', actor['character']))

        self.connection.commit()


    def update_worker_from_json(self, json_file):
        with open(json_file, 'r', encoding='utf-8') as file:
            workers = json.load(file)

        with self.connection.cursor() as cursor:
            for worker in tqdm(workers, desc="Updating Workers info: "):
                sql_query = """
                UPDATE worker
                SET birth = %s,
                    avatar = %s,
                    srcset = %s,
                    bio = %s,
                    job = %s
                WHERE id = %s AND name = %s and imdbID=%s
                """
                cursor.execute(sql_query, (
                    worker.get('birth'),
                    worker.get('avatar'),
                    worker.get('srcset'),
                    worker.get('bio'),
                    worker.get('job'),
                    worker.get('id'),
                    worker.get('name'),
                    worker.get('imdbID')
                ))
        self.connection.commit()

    def load_user_from_json(self, json_file):
        with open(json_file, 'r', encoding='utf-8') as file:
            users = json.load(file)

        with self.connection.cursor() as cursor:
            for user in tqdm(users, desc="Inserting users into database"):
                sql_query = """
                INSERT INTO user (id, avatar, username, password, email, bio, birthday)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    avatar = VALUES(avatar),
                    username = VALUES(username),
                    password = VALUES(password),
                    email = VALUES(email),
                    bio = VALUES(bio),
                    birthday = VALUES(birthday);
                """
                cursor.execute(sql_query, (
                    user['id'],
                    user['avatar'],
                    user['username'],
                    user['password'],
                    user['email'],
                    user['bio'],
                    user['birthday']
                ))
        self.connection.commit()

    def load_review_from_json(self, json_file):
        with open(json_file, 'r', encoding='utf-8') as file:
            reviews = json.load(file)

        with self.connection.cursor() as cursor:
            for movie_title, movie_reviews in tqdm(reviews.items(), desc="Inserting reviews into database"):
                cursor.execute("SELECT id FROM movie WHERE title = %s", (movie_title,))
                movie_result = cursor.fetchone()
                movie_id = movie_result['id']

                for review in movie_reviews:
                    cursor.execute("SELECT id FROM user WHERE username = %s", (review['author'],))
                    user_result = cursor.fetchone()
                    user_id = user_result['id']
                    sql_query = """
                    INSERT INTO review (id, movie_id, user_id, content, writer_id, likes, date, rating)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        movie_id = VALUES(movie_id),
                        user_id = VALUES(user_id),
                        content = VALUES(content),
                        writer_id = VALUES(writer_id),
                        likes = VALUES(likes),
                        date = VALUES(date),
                        rating = VALUES(rating);
                    """
                    cursor.execute(sql_query, (
                        'rev_' + str(uuid.uuid4())[:10],
                        movie_id,
                        None,
                        review['text'],
                        user_id,
                        0,
                        review['date'],
                        review['rating']
                    ))
        self.connection.commit()

    def updating_movie_rating_from_reviews(self):
        with self.connection.cursor() as cursor:
            query = """
            SELECT writer_id, movie_id, rating FROM review;
            """
            cursor.execute(query)
            rating_info = cursor.fetchall()

        with self.connection.cursor() as cursor:
            for info in rating_info:
                query = """
                INSERT INTO user_movie_rating (user_id, movie_id, rating)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                rating = VALUES(rating);
                """
                cursor.execute(query, (info['writer_id'], info['movie_id'], info['rating']))
        self.connection.commit()

    def update_local_rating(self):
        with self.connection.cursor() as cursor:
            query = """
            SELECT id FROM movie;
            """
            cursor.execute(query)
            movies = cursor.fetchall()

            for movie in movies:
                query = """
                SELECT AVG(rating) FROM user_movie_rating WHERE movie_id=%s;
                """
                cursor.execute(query, movie['id'])
                avg = cursor.fetchone()
                query = """
                UPDATE movie SET local_rating=%s WHERE id=%s;
                """
                cursor.execute(query, (avg['AVG(rating)'], movie['id']))
        self.connection.commit()