from module import IMDb, DataBase, PersonScraper

if __name__ == "__main__":
    imdb = IMDb()
    # movies = imdb.fetch_top_250_movies()
    # imdb.to_json(movies, 'data/movies/imdb_top_250_movies.json')
    
    db = DataBase(host='localhost', password='Pyf20030317', database='ustcMDb')
    db.connect_db()
    # workers = imdb.fetch_all_casts_info_from_db(db.connection)
    # imdb.to_json(workers, "/home/yufengpeng-wsl/UstcMDb/data/workers/workers.json")
    # db.load_movie_from_json('/home/yufengpeng-wsl/UstcMDb/data/movies/imdb_top_250_movies.json')
    db.update_worker_from_json(json_file="data/workers/workers.json")
