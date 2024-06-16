from module import IMDb, DataBase, PersonScraper, ReviewScraper, User

if __name__ == "__main__":
    imdb = IMDb()
    # movies = imdb.fetch_top_250_movies()
    # imdb.to_json(movies, 'data/movies/imdb_top_250_movies.json')
    
    db = DataBase(host='localhost', password='zhangzhe777', database='ustcMDb')
    # workers = imdb.fetch_all_casts_info_from_db(db.connection)
    # imdb.to_json(workers, "/home/yufengpeng-wsl/UstcMDb/data/workers/workers.json")
    # db.load_movie_from_json('data\movies\imdb_top_250_movies.json')
    # db.update_worker_from_json(json_file="data/workers/workers.json")

    # scraper = ReviewScraper()
    # reviews = scraper.fetch_all_reviews(db.connection)
    # imdb.to_json(reviews, 'data/reviews/reviews.json')

    # user = User()

    # users = user.create_user_from_views(reviews="data/reviews/reviews.json")

    # imdb.to_json(users, "data/users/users.json")

    # db.load_user_from_json("data/users/users.json")
    # db.load_review_from_json("data/reviews/reviews.json")