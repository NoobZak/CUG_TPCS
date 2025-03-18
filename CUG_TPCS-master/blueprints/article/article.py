from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from decorator import login_required
from models import Article
from exts import db
import cmarkgfm
from cmarkgfm.cmark import Options
from flask_paginate import Pagination, get_page_parameter

article = Blueprint('article', __name__, url_prefix='/article', template_folder='templates/article')


def markdown(md):
    return cmarkgfm.github_flavored_markdown_to_html(
        md,
        options=(Options.CMARK_OPT_UNSAFE | Options.CMARK_OPT_GITHUB_PRE_LANG)
    )


@article.route('/')
def index():
    # 分页处理
    pageSize = 10
    page = request.args.get(get_page_parameter(), type=int, default=1)  # 获取页码，默认为1
    start = (page - 1) * pageSize
    # 文章总数
    total = Article.query.count()
    pagination = Pagination(bs_version=5, css_framework='bootstrap5', page=page, total=total)
    articleList = db.session.query(Article).order_by(Article.id.desc()).limit(pageSize).offset(start).all()

    # 文章内容显示长度不超过500个字符
    for article in articleList:
        if len(article.content) >= 500:
            article.content = article.content[:495] + '  ...'

    totalPages = total // pageSize if total % pageSize == 0 else total // pageSize + 1
    pageInfo = {"nowPage": page, "pageSize": pageSize, "totalPages": totalPages, "total": total}

    return render_template('article/article.html', articleList=articleList, pageInfo=pageInfo, pagination=pagination)


@article.route('/add', methods=['GET', 'POST'])
@login_required
def add_article():
    if request.method == 'GET':
        return render_template('article/add_article.html')
    if request.method == 'POST':
        if request.form is not None:
            if request.form['title'] == "":
                flash("文章标题为空", "warning")
                return render_template('article/add_article.html')
            title = request.form['title']
            if request.form['content'] == "":
                flash("文章内容为空", "warning")
                return render_template('article/add_article.html')
            content = request.form['content']
            author = g.userid
            article = Article(title, content, author)
            db.session.add(article)
            db.session.commit()
            flash("发布成功", "success")

            return redirect('/article')

        else:
            flash("不能发布空的内容", "warning")
            return render_template('article/add_article.html')


@article.route('/<int:article_id>', methods=['GET', 'POST'])
@login_required
def detail_article(article_id):
    article = Article.query.get_or_404(article_id)
    if request.method == 'GET':
        return render_template('article/detail_article.html', title=article.title,
                               content=markdown(article.content),
                               author=article.author)
