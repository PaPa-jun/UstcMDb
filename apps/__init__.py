from flask import Flask, g, session
from apps.config import config_map
from extensions import DataBase
from apps.main import blueprint as main_bp
from apps.user import blueprint as user_bp
from apps.movie import blueprint as movie_bp
from apps.menu import blueprint as menu_bp

def create_app(mode="default"):
    app = Flask(__name__, template_folder="../templates", static_folder="../assets")
    app.config.from_object(config_map[mode])

    db = DataBase()
    db.init_app(app=app)

    @app.before_request
    def init():
        # 初始化数据库
        db.init_db(schema_path="schema.sql")

        # 加载用户信息
        user_id = session.get('user_id')
        if user_id is None:
            g.current_user = None
        else:
            with g.db.cursor() as cursor:
                cursor.execute('SELECT id, username FROM user WHERE id=%s', (user_id))
                g.current_user = cursor.fetchone()

    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(movie_bp, url_prefix="/movie")
    app.register_blueprint(menu_bp, url_prefix="/menu")
    
    return app