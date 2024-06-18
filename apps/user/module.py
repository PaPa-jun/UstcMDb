from flask import g, session
from werkzeug.security import check_password_hash, generate_password_hash
import uuid

class Auth:
    """
    用户认证
    """
    def __init__(self, mode, request) -> None:
        self.mode = mode
        self.error = None
        self.init(request)

    def init(self, request):
        if self.mode == "login":
            self.username = request.form.get("username")
            self.password = request.form.get("password")
            self.login()
        elif self.mode == "register":
            self.username = request.form.get("username")
            self.email = request.form.get("email")
            self.password = request.form.get("password")
            self.confirm_password = request.form.get("confirmpassword")
            self.register()

    def login(self):
        with g.db.cursor() as cursor:
            cursor.execute('SELECT id, username, password FROM user WHERE username=%s', (self.username))
            user = cursor.fetchone()

        if user is None or not check_password_hash(user['password'], self.password):
            self.error = '用户名或密码错误！'
        else:
            session.clear()
            session['user_id'] = user['id']

    def register(self):
        if not self.username:
            self.error = '用户名不能为空！'
        elif not self.email:
            self.error = '邮箱不能为空！'
        elif not self.password:
            self.error = '密码不能为空！'
        elif self.password != self.confirm_password:
            self.error = '两次输入密码不匹配！'

        if self.error is None:
            with g.db.cursor() as cursor:
                cursor.execute('SELECT id FROM user WHERE username=%s', (self.username))
                if cursor.fetchone() is not None:
                    self.error = f"用户：{self.username} 已存在！"
                
                cursor.execute('SELECT id FROM user WHERE email=%s', (self.email))
                if cursor.fetchone() is not None:
                    self.error = f"该邮箱 {self.email} 已注册！"

            if self.error is None:
                hashed_password = generate_password_hash(self.password)
                user_id = 'usr_' + str(uuid.uuid4())[:10]  # Generate a unique ID with 'usr_' prefix and 10-digit UUID
                with g.db.cursor() as cursor:
                    cursor.execute('''
                        INSERT INTO user (id, username, email, password, avatar) 
                        VALUES (%s, %s, %s, %s, '/images/avatars/fixed_pics/default.jpg')
                    ''', (user_id, self.username, self.email, hashed_password))
                    g.db.commit()
