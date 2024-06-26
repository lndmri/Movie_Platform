from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from flask_login import login_required, current_user
import json


views = Blueprint('views', __name__)

@views.route('/',  methods=['GET','POST'])
def home():
    if "userid" in session:
        firstname = session['firstname']
    else:
        return redirect(url_for('auth.login'))
    return render_template('user_home.html', firstname=firstname)

@views.route('/user_home')
def user_home():
    if "userid" in session:
        firstname = session['firstname']
    else:
        return redirect(url_for('auth.login'))
    return render_template('user_home.html', firstname=firstname)

@views.route('/favorites')
def favorites():
    if "userid" in session:
        firstname = session['firstname']
    else:
        return redirect(url_for('auth.login'))
    return render_template('favorites.html')

@views.route('/my-movies')
def my_movies():
    if "userid" in session:
        firstname = session['firstname']
    else:
        return redirect(url_for('auth.login'))
    return render_template('my_movies.html')

@views.route('/history')
def history():
    if "userid" in session:
        firstname = session['firstname']
    else:
        return redirect(url_for('auth.login'))
    return render_template('history.html')

@views.route('/account')
def account():
    if "userid" in session:
        firstname = session['firstname']
    else:
        return redirect(url_for('auth.login'))
    return render_template('account.html')


