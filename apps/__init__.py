from flask import Flask, g, session
from apps.config import config_map
from extensions import DataBase
from apps.main import blueprint as main_bp
from apps.user import blueprint as user_bp

def create_app(mode="default"):
    app = Flask(__name__, template_folder="../templates", static_folder="../assets")
    app.config.from_object(config_map[mode])

    db = DataBase()
    db.init_app(app=app)

    @app.before_request
    def init():
        # 初始化数据库
        db.init_db(schema_path="extensions/mysql/schema.sql")

        # 加载用户信息
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            with g.db.cursor() as cursor:
                cursor.execute('SELECT id, username, email FROM user WHERE id=%s', (user_id,))
                g.user = cursor.fetchone()

    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix="/user")
    
    return app