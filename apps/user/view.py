from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from apps.user.module import Auth

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
    return render_template("./user/profile.html")