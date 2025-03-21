from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from decorator import login_required
from models import User, Article
from exts import db
import random
import string
from hashlib import md5
from flask_paginate import Pagination, get_page_parameter

user = Blueprint('user', __name__, url_prefix='/user', template_folder='templates/user')


def hash_password(password, salt=None):
    if salt is None:
        salt = ''.join(random.sample(string.ascii_letters + string.digits, 4))
    return salt + '$' + md5((password + salt).encode()).hexdigest()


def change_user(new_username="", new_studentid="", current_password="", new_password=""):
    currentuserid = g.userid
    user = User.query.get(currentuserid)
    if new_username != "" and user.username != new_username:
        user.username = new_username
    if new_studentid != "" and user.studentid != new_studentid:
        user.studentid = new_studentid
    if new_password != "":
        if current_password != "":
            salt = user.passwdhash[:4]
            Hash = user.passwdhash[5:]
            if Hash == md5((current_password + salt).encode()).hexdigest():
                new_password_hash = hash_password(new_password)
                user.passwdhash = new_password_hash
            else:
                flash(message="当前密码错误", category="warning")
        else:
            flash(message="请输入当前密码", category="warning")
    db.session.commit()


@user.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'GET':
        user = User.query.filter_by(id=g.userid).first()

        pageSize = 6
        page = request.args.get(get_page_parameter(), type=int, default=1)  # 获取页码，默认为1
        start = (page - 1) * pageSize
        # 文章总数
        total = Article.query.filter_by(author_id=g.userid).count()
        pagination = Pagination(bs_version=5, css_framework='bootstrap5', page=page, total=total)
        articleList = db.session.query(Article).filter_by(author_id=g.userid).order_by(Article.id.desc()).limit(
            pageSize).offset(start).all()

        # 文章内容显示长度不超过500个字符
        for article in articleList:
            if len(article.content) >= 300:
                article.content = article.content[:295] + '  ...'

        totalPages = total // pageSize if total % pageSize == 0 else total // pageSize + 1
        pageInfo = {"nowPage": page, "pageSize": pageSize, "totalPages": totalPages, "total": total}

        return render_template('user/user.html', user=user, articleList=articleList, pageInfo=pageInfo,
                               pagination=pagination)
    if request.method == 'POST':
        new_username = request.form['username']
        new_studentid = request.form['studentid']
        new_password = request.form['password']
        current_password = request.form['current_password']
        reguser = User.query.filter_by(username=new_username).first()
        if reguser is None:
            change_user(new_username, new_studentid, current_password, new_password)
            flash("修改成功 请重新登陆", "success")
            return redirect(url_for('logout'))
        else:
            flash("用户名已被注册", "warning")


@user.route('/<string:user_name>')
@login_required
def userinfo(user_name):
    user = User.query.filter_by(username=user_name).first()

    pageSize = 6
    page = request.args.get(get_page_parameter(), type=int, default=1)  # 获取页码，默认为1
    start = (page - 1) * pageSize
    # 文章总数
    total = Article.query.filter_by(author_id=user.id).count()
    pagination = Pagination(bs_version=5, css_framework='bootstrap5', page=page, total=total)
    articleList = db.session.query(Article).filter_by(author_id=user.id).order_by(Article.id.desc()).limit(pageSize).offset(start).all()

    # 文章内容显示长度不超过500个字符
    for article in articleList:
        if len(article.content) >= 300:
            article.content = article.content[:295] + '  ...'

    totalPages = total // pageSize if total % pageSize == 0 else total // pageSize + 1
    pageInfo = {"nowPage": page, "pageSize": pageSize, "totalPages": totalPages, "total": total}

    return render_template('user/user.html', user=user, articleList=articleList, pageInfo=pageInfo,
                           pagination=pagination)
