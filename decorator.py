from functools import wraps
from flask import g, redirect, session, url_for,flash


# 登录拦截器
def login_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if g.username is None:
            flash("请先登录", "warning")
            return redirect(url_for('login'))
        else:
            return f(*args, **kwargs)

    return inner
