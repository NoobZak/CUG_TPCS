'''
项目基础文件，包含了登录和注册的后端逻辑
'''

from flask import Flask, render_template, request, flash, redirect, url_for, session, g
from flask_sqlalchemy import SQLAlchemy
import random
import string
from hashlib import md5
from flask_migrate import Migrate

from exts import db
from models import User
import settings

from blueprints.challenges.challenges import challenges as challenges_bp
from blueprints.article.article import article as article_bp
from blueprints.user.user import user as user_bp
from blueprints.calendar.calendar import calendar as calendar_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{settings.MySQL_USERNAME}:{settings.MySQL_PASSWORD}@{settings.MySQL_HOSTNAME}:{settings.MySQL_PORT}/tpcs?charset=utf8mb4"
# db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

# 注册蓝图
app.register_blueprint(challenges_bp)
app.register_blueprint(article_bp)
app.register_blueprint(user_bp)
app.register_blueprint(calendar_bp)


def hash_password(password, salt=None):
    if salt is None:
        salt = ''.join(random.sample(string.ascii_letters + string.digits, 4))
    return salt + '$' + md5((password + salt).encode()).hexdigest()


def add_user(username, studentid, passwdhash, permission):
    user = User(username, studentid, passwdhash, permission)
    db.session.add(user)
    db.session.commit()


with app.app_context():
    db.create_all()
    adminuser = User.query.filter_by(username=settings.ADMIN_USERNAME).all()
    if not adminuser:
        # creat default admin
        adminusername = settings.ADMIN_USERNAME
        adminpasswd = settings.ADMIN_PASSWORD
        salt = '0X3F'
        add_user(adminusername, '1', hash_password(adminpasswd, salt), 1)


# check session
@app.before_request
def before_request():
    username = session.get('username')
    userid = session.get('userid')
    if username is None or userid is None:
        setattr(g, "username", None)
        setattr(g, "userid", None)
    else:
        setattr(g, "username", username)
        setattr(g, "userid", userid)


@app.context_processor
def inject_username():
    return dict(username=g.username)


@app.route('/')  # index page
def index():
    return render_template('index.html')


@app.route('/tutorial', methods=['GET'])
def tutorial():
    return render_template('tutorial.html')


@app.route('/scoreboard', methods=['GET'])
def scoreboard():
    users = User.query.order_by(User.score.desc()).all()
    return render_template('challenges/scoreboard.html', users=users)


@app.route('/login', methods=['GET', 'POST'])  # login page
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        finduser = User.query.filter_by(username=username).first()
        if finduser:
            salt = finduser.passwdhash[:4]
            hash = finduser.passwdhash[5:]
            if hash == md5((password + salt).encode()).hexdigest():
                # set session for checking
                session['userid'] = finduser.id
                session['username'] = username
                flash(message="登陆成功", category="success")
                return redirect(url_for('index'))
            else:
                flash(message="用户密码错误", category="warning")
        else:
            flash(message="未找到该用户", category="warning")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])  # register page
def register():
    if request.method == 'POST':
        username = request.form['username']
        studentid = request.form['studentid']
        password = request.form['password']
        reguser = User.query.filter_by(username=username).first()
        if reguser is None:
            add_user(username, studentid, hash_password(password), 0)
            flash("注册成功", "success")
            return redirect(url_for('login'))
        else:
            flash("用户名已被注册", "warning")
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("用户已登出", "success")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.debug = settings.DEBUG
    app.run(host='0.0.0.0', port=5000)
