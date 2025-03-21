from datetime import datetime

from exts import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    studentid = db.Column(db.String(12), nullable=False)
    passwdhash = db.Column(db.String(70), nullable=False)
    permission = db.Column(db.Boolean, nullable=False)
    score = db.Column(db.Integer, nullable=False)

    def __init__(self, username, studentid, passwdhash, permission):
        self.username = username
        self.studentid = studentid
        self.passwdhash = passwdhash
        self.permission = permission
        self.score = 0

    def __repr__(self):
        return f"<User {self.username}>"


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('articles', lazy=True))

    def __init__(self, title, content, author_id):
        self.title = title
        self.content = content
        self.author_id = author_id

    def __repr__(self):
        return f"<Article {self.title}>"


class Challenge(db.Model):
    __tablename__ = 'challenge'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    show = db.Column(db.Boolean, nullable=False)
    docker_name = db.Column(db.String(50), nullable=True)
    flag = db.Column(db.String(50), nullable=False)

    def __init__(self, title, content, type, score, show, docker_name, flag):
        self.title = title
        self.content = content
        self.type = type
        self.score = score
        self.show = show
        self.docker_name = docker_name
        self.flag = flag

    def __repr__(self):
        return f"<Challenge {self.title}>"


class Calendar(db.Model):
    __tablename__ = 'calendar'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(100), nullable=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)

    def __init__(self, title, url, start, end):
        self.title = title
        self.url = url
        self.start = start
        self.end = end

    def __repr__(self):
        return f"<Calendar {self.title}>"
