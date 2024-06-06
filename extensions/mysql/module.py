import pymysql
from flask import g

class DataBase:
    """
    数据库
    """

    def __init__(self) -> None:
        pass

    def init_app(self, app):
        app.teardown_appcontext(self.close_db)
        self.host = app.config.get("SQL")["host"]
        self.port = app.config.get("SQL")["port"]
        self.user = app.config.get("SQL")["user"]
        self.password = app.config.get("SQL")["password"]
        self.schema = app.config.get("SQL")["schema"]
        self.charset = app.config.get("SQL")["charset"]

    def connect_db(self):
        db = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.schema,
            charset=self.charset,
            cursorclass=pymysql.cursors.DictCursor
        )
        return db
    
    def get_db(self):
        if 'db' not in g:
            g.db = self.connect_db()
        return g.db

    def close_db(self, e=None) -> None:
        db = g.pop('db', None)
        if db is not None:
            db.close()

    def init_db(self, schema_path):
        db = self.get_db()
        with open(schema_path, 'r') as f:
            sql = f.read()
        sql_commands = sql.split(";")
        with db.cursor() as cursor:
            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)
        db.commit()