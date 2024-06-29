from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from flask_login import login_required, current_user
from .helpers import db_conn
import psycopg2, psycopg2.extras
import json


views = Blueprint('views', __name__)

@views.route('/',  methods=['GET','POST'])
@views.route('/user_home')
def home():
    if "userid" in session:
        firstname = session['firstname']
        print()
    else:
        return redirect(url_for('auth.login'))
    # We get to this return statement if the user is logged in already
    return render_template('home.html', firstname=firstname)

# Proposed Change 1: Why do we need two functions if they are doing exactly the same
# My proposed change is to merge them. BY adding decorator @views.route('/user_home') to the first function

# @views.route('/user_home')
# def user_home():
#     if "userid" in session:
#         firstname = session['firstname']
#     else:
#         return redirect(url_for('auth.login'))
#     return render_template('user_home.html', firstname=firstname)

# Route for movie searching (this is a route onlu as we will be showing the content in the home page)
@views.route('/search', methods = ["POST", "GET"])
def search():
    # db connection
    conn = db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # LOGIC: the logic followed were is that the /search route is invoked as POST request (done by AJAX) then we
    # do search. In the AJAX request we
    
    if request.method == "POST":
        if 'query' in request.form:
            search_word = request.form['query']
            print(search_word)
            if search_word == '':
                cur.execute("SELECT * FROM Movies ORDER BY Score")
                results = cur.fetchall()
            else:
                cur.execute("""
                    SELECT m.* FROM Movies m
                    WHERE m.title ILIKE %s
                    OR m.movieID IN 
                    (SELECT movieID FROM Works w, Actors a 
                    WHERE w.actorID = a.actorID AND a.name ILIKE %s)
                    OR m.movieID IN 
                    (SELECT movieID FROM Directs d, Directors di
                    WHERE d.dirID = di.dirID AND di.name ILIKE %s)
                    ORDER BY m.score
                    """, ('%' + search_word + '%','%' + search_word + '%','%' + search_word + '%',))

                numrows = int(cur.rowcount)
                results = cur.fetchall()
                print(results)

    return jsonify({'htmlresponse': render_template('response.html', results=results, numrows=numrows)})

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


