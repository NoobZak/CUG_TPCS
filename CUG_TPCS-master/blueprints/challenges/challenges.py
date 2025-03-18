from dominate.tags import form
from flask import Blueprint, render_template, send_file, url_for, g, flash, request, redirect
from decorator import login_required
from flask_paginate import Pagination, get_page_parameter
from models import User, Challenge
from exts import db
import settings
import os

challenges = Blueprint(name='challenges', url_prefix='/challenges', import_name=__name__,
                       template_folder='templates/challenges')


@challenges.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        userid = g.userid
        user = User.query.filter_by(id=userid).first()
        challengeid = list(request.form.keys())[0][5:]
        challenge = Challenge.query.filter_by(id=challengeid).first()
        user_flag = request.form.get("flag-" + challengeid)
        flag = challenge.flag
        if user_flag == flag:
            user.score += challenge.score
            flash(message='回答正确', category='success')
            db.session.commit()
        else:
            flash(message='回答错误', category='warning')
    userper = User.query.filter_by(id=g.userid).first().permission
    challenges = Challenge.query.all()
    types = []
    for challenge in challenges:
        if challenge.type not in types:
            types.append(challenge.type)

    return render_template('challenges/challenges.html', challenges=challenges, types=types, userper=userper)


@challenges.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    user = User.query.filter_by(id=g.userid).first()
    if not user.permission:
        flash(message="无权访问，请联系管理员！", category='warning')
        return redirect('/challenges')
    if user.permission:
        if request.method == 'POST':
            id = request.form['id']
            challenge = Challenge.query.filter_by(id=id).first()
            if request.form['title'] != '':
                challenge.title = request.form['title']
            if request.form['type'] != '':
                challenge.type = request.form['type']
            if request.form['content'] != '':
                challenge.content = request.form['content']
            if request.form['score'] != '':
                challenge.score = request.form['score']
            if request.form['docker_name'] != '':
                challenge.docker_name = request.form['docker_name']
            if request.form['flag'] != '':
                challenge.flag = request.form['flag']
            if 'show' in request.form:
                challenge.show = True
            db.session.commit()

        pageSize = 10
        page = request.args.get(get_page_parameter(), type=int, default=1)
        start = (page - 1) * pageSize
        total = Challenge.query.count()
        pagination = Pagination(bs_version=5, css_framework='bootstrap5', page=page, total=total)
        challenges = db.session.query(Challenge).order_by(Challenge.id.desc()).limit(pageSize).offset(start).all()

        totalPages = total // pageSize if total % pageSize == 0 else total // pageSize + 1
        pageInfo = {"nowPage": page, "pageSize": pageSize, "totalPages": totalPages, "total": total}
        return render_template('challenges/manage.html', challenges=challenges, pageInfo=pageInfo,
                               pagination=pagination)


@challenges.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    user = User.query.filter_by(id=g.userid).first()
    if not user.permission:
        flash(message="无权访问，请联系管理员！", category='warning')
        return redirect('/challenges')
    else:
        if request.method == 'GET':
            return render_template('challenges/add_challenge.html')
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            Type = request.form['type']
            score = request.form['score']
            docker_name = request.form['docker_name']
            flag = request.form['flag']
            if request.files['file'].filename != '':
                file = request.files['file']
                basepath = os.path.dirname(settings.CHALLENGE_DIR)
                filepath = os.path.join(basepath, 'challenges', Type, title)
                if not os.path.exists(filepath):
                    os.makedirs(filepath)
                file.save(filepath + '\\' + file.filename)
            else:
                file = None
            if 'show' in request.form:
                show = True
            else:
                show = False

            challenge = Challenge(title=title, content=content, type=Type, score=score, docker_name=docker_name,
                                  show=show, flag=flag)
            db.session.add(challenge)
            db.session.commit()
            flash(message="添加成功", category='success')
            return redirect('/challenges/manage')
        return render_template('challenges/add_challenge.html')


@challenges.route('/delete/<int:challenge_id>', methods=['GET'])
@login_required
def delete(challenge_id):
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    db.session.delete(challenge)
    db.session.commit()
    flash(message="删除成功", category='success')
    return redirect('/challenges/manage')


@challenges.route('/download/<int:challenge_id>')
@login_required
def download(challenge_id):
    file_path = 'challenges\\Web\\web1\\test.txt'
    return send_file(file_path, as_attachment=True)
