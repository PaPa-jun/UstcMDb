from module import Scraper, DataBase, User

path_top_25 = "data/movies/imdb_top_25_movies.json"
path_popular_25 = "data/movies/imdb_popular_25_movies.json"
path_top_india = "data/movies/imdb_top_india_movies.json"
path_casts = "data/casts/casts.json"
path_reviews = "data/reviews/reviews.json"
path_users = "data/users/users.json"

def main():
    scraper = Scraper()
    database = DataBase("localhost", "Pyf20030317", "ustcMDb")
    user = User()
    india_movies = scraper.movie_scraper.fetch_india_movies()
    scraper.to_json(india_movies, path_top_india)
    top_movies = scraper.movie_scraper.fetch_top_25_movies()
    scraper.to_json(top_movies, path_top_25)
    popular_movies = scraper.movie_scraper.fetch_popular_25_movies()
    scraper.to_json(popular_movies, path_popular_25)

    database.load_movie_from_json(path_top_25)
    database.load_movie_from_json(path_popular_25)
    database.load_movie_from_json(path_top_india)

    update_casts = scraper.cast_scraper.fetch_all_casts_info_from_db(database.connection)
    scraper.to_json(update_casts, path_casts)
    database.update_worker_from_json(path_casts)

    reviews = scraper.review_scraper.fetch_all_reviews(database.connection)
    scraper.to_json(reviews, path_reviews)
    fake_users = user.create_user_from_reviews(path_reviews)
    scraper.to_json(fake_users, path_users)
    database.load_user_from_json(path_users)
    database.load_review_from_json(path_reviews)

if __name__ == "__main__":
    main()