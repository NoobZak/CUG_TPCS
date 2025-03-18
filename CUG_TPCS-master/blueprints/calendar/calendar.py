from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from decorator import login_required
from models import Article
from exts import db

calendar = Blueprint('calendar', __name__, url_prefix='/calendar',template_folder='templates/calendar')

@calendar.route('/')
def index():
    return render_template('calendar/calendar.html')