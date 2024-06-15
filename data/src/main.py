from module import IMDb, DataBase

if __name__ == "__main__":
    # imdb = IMDb()
    # movies = imdb.fetch_top_250_movies()
    # imdb.to_json(movies, 'data\movies\imdb_top_250_movies.json')
    
    db = DataBase(host='localhost', password='zhangzhe777', database='ustcMDb')
    connection = db.connect_db()
    db.load_json_into_db('data/movies/imdb_top_250_movies.json', connection)
    # print(imdb.search_person('Benedict Cumberbatch'))