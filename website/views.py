from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import json


views = Blueprint('views', __name__)

@views.route('/',  methods=['GET','POST'])
def home():
    return render_template('base.html')

@views.route('/favorites')
def favorites():
    return render_template('favorites.html')

@views.route('/my-movies')
def my_movies():
    return render_template('my_movies.html')

@views.route('/history')
def history():
    return render_template('history.html')

@views.route('/account')
def account():
    return render_template('account.html')


