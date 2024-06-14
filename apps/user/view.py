from flask import Blueprint, render_template, flash, redirect, url_for, request, session, g
from apps.user.module import Auth
from extensions import User
import os

blueprint = Blueprint("user", __name__)

@blueprint.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        auth = Auth("login", request)
        if auth.error:
            print(auth.error)
            flash(auth.error)
            return render_template("/user/login.html")
        
        return redirect(url_for('main.index', username=auth.username))

    return render_template("/user/login.html")

@blueprint.route('/logout')
def logout():
    session.clear()
    flash('你已登出！')
    return redirect(url_for('main.index'))

@blueprint.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        auth = Auth("register", request)
        if auth.error:
            print(auth.error)
            flash(auth.error)
            return render_template("/user/register.html")
        print("注册成功，请登录！")
        flash("注册成功，请登录！")
        return redirect(url_for('user.login'))

    return render_template("/user/register.html")

@blueprint.route("/profile")
def profile():
    # 加载用户信息
    current_user = User(g.current_user['id'])

    current_user.get_info(g.db)
    return render_template("./user/profile.html", current_user = current_user)

@blueprint.route("/profile/modify", methods=['GET', 'POST'])
def profile_modify():
    current_user = User(g.current_user['id'])
    current_user.get_info(g.db)
    
    if request.method == 'POST':
        new_avatar = request.files['avatar']
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        new_bio = request.form.get('bio')
        new_birthday = request.form.get('birthday')
        
        if new_username != '':
            current_user.update_info(g.db, 'username', new_username)
        if new_email != '':
            current_user.update_info(g.db, 'email', new_email)
        if new_bio != '':
            current_user.update_info(g.db, 'bio', new_bio)
        if new_birthday != '':
            current_user.update_info(g.db, 'birthday', new_birthday)
        if new_avatar and new_avatar.filename != '':
            if new_avatar.filename.split('.')[-1].lower() in ['png', 'jpg', 'jpeg', 'bmp']:
                save_path = os.path.join(os.path.dirname(__file__), "../../assets/images/avatars/", g.current_user['id'] + '.' + new_avatar.filename.split('.')[-1])
                new_avatar.save(save_path)
                current_user.update_info(g.db, 'avatar', 'images/avatars/' + g.current_user['id'] + '.' + new_avatar.filename.split('.')[-1])
            else:
                flash('请传入正确的文件格式（png, jpg, jpeg, bmp）')

        return redirect(url_for('user.profile'))

    return render_template('user/profile_modify.html', current_user = current_user)