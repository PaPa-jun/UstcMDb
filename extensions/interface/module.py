class User:
    """
    用户对象
    """
    def __init__(self, id) -> None:
        self.id = id

    def get_info(self, db):
        with db.cursor() as cursor:
            cursor.execute('SELECT username, avatar, email, bio, birthday FROM user WHERE id=%s', (self.id))
            current_user = cursor.fetchone()

        self.username = current_user['username']
        self.avatar = current_user['avatar']
        self.email = current_user['email']
        self.bio = current_user['bio']
        self.birthday = current_user['birthday']

    def update_info(self, db, item_name, content):
        if item_name not in ['username', 'avatar', 'email', 'bio', 'birthday']:
            raise ValueError("Invalid item name")

        query = f"UPDATE user SET {item_name} = %s WHERE id = %s"

        with db.cursor() as cursor:
            cursor.execute(query, (content, self.id))
            db.commit()