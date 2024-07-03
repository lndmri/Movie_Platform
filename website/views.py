from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from flask_login import login_required, current_user
from .helpers import db_conn
import psycopg2
import psycopg2.extras
import json


views = Blueprint('views', __name__)


@views.route('/',  methods=['GET', 'POST'])
@views.route('/user_home')
def home():
    if "userid" in session:
        firstname = session['firstname']
        print()
    else:
        return redirect(url_for('auth.login'))
    # We get to this return statement if the user is logged in already
    return render_template('home.html', firstname=firstname)

# Route for movie searching (this is a route only as we will be showing the content in the home page)


@views.route('/search', methods=["POST", "GET"])
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
                    ORDER BY m.score DESC
                    """, ('%' + search_word + '%', '%' + search_word + '%', '%' + search_word + '%',))

                numrows = int(cur.rowcount)
                results = cur.fetchall()
                print(results)

            conn.close()
            cur.close()

    return jsonify({'htmlresponse': render_template('response.html', results=results, numrows=numrows)})


@views.route('/favorites', methods=["GET"])
def favorites():
    if "userid" in session:
        conn = db_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("""SELECT m.title FROM Movies m, Favorites f
                                WHERE m.movieID = f.movieID
                                AND userID = %s
                                ORDER BY f.time""", (session['userid'],))

        favorites = cur.fetchall()

    else:
        return redirect(url_for('auth.login'))

    conn.close()
    cur.close()
    return render_template('favorites.html', favorites=favorites)


@views.route('/my-movies', methods=["GET"])
def my_movies():
    if "userid" in session:
        conn = db_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("""SELECT m.* FROM Movies m, Owns o
                                WHERE m.movieID = o.movieID 
                                AND userID = %s
                                ORDER BY o.time""", (session['userid'],))

        paid_movies = cur.fetchall()

    else:
        return redirect(url_for('auth.login'))
    return render_template('my_movies.html', paid_movies=paid_movies)


@views.route('/history')
def history():
    if "userid" in session:
        firstname = session['firstname']
    else:
        return redirect(url_for('auth.login'))
    return render_template('history.html')


@views.route('/details/<int:movieID>', methods=['GET'])
def details(movieID):
    if "userid" in session:
        # db connection
        conn = db_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute('SELECT * FROM Movies WHERE movieID = %s', (movieID,))
        movie = cur.fetchone()

        cur.execute("""SELECT directors.name FROM Directors, Directs 
                    WHERE directors.dirid = directs.dirid
                    AND movieID = %s""", (movieID,))
        directors = cur.fetchall()

        cur.execute("""SELECT actors.name FROM Actors, Works 
                    WHERE actors.actorid = works.actorid
                    AND movieID = %s""", (movieID,))
        actors = cur.fetchall()

    else:
        return redirect(url_for('auth.login'))

    cur.close()
    conn.close()
    return render_template('details.html', movie=movie, directors=directors, actors=actors)


@views.route('/add_to_favorites', methods=['POST'])
def add_to_favorites():
    userId = session['userid']
    movieId = request.form.get('movieid')

    conn = db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute(
        """INSERT INTO favorites (userid, movieid) VALUES (%s, %s)""", (userId, movieId))
    conn.commit()
    message = 'Movie added to favorites!'
    cur.close()
    conn.close()

    return jsonify({'message': message})


@views.route('/remove_favorite', methods=["POST"])
def remove_favorite():
    userId = session['userid']
    movieId = request.form.get('favorite_title')

    conn = db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute(
        """DELETE FROM favorites WHERE movieid IN (SElECT movieid FROM movies m WHERE m.title = %s) AND userid = %s""", (movieId, userId,))
    conn.commit()
    message = 'Movie removed from favorites!'
    cur.close()
    conn.close()

    return redirect(url_for('views.favorites'))


@views.route('/account', methods=["GET"])
def account():
    if "userid" in session:
        conn = db_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("""SELECT * FROM Users
                        WHERE userID = %s """, (session['userid'],))
        results = cur.fetchone()

    else:
        return redirect(url_for('auth.login'))

    conn.close()
    cur.close()
    return render_template('account.html', results=results)

@views.route('/add_cash', methods=['GET', 'POST'])
def add_cash():
    if "userid" in session:
        conn = db_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cur.execute("""SELECT * FROM Users
                    WHERE userID = %s """, (session['userid'],))
        
        user = cur.fetchone()

    else:
        return redirect(url_for('auth.login'))
    
    conn.close()
    cur.close()
    return render_template('add_cash.html', user=user )

@views.route('/update_cash', methods=['GET','POST'])
def update_cash():
    # db connection
    conn = db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == "POST":
        if 'new_balance' in request.form:
            new_balance = request.form['new_balance']             
            cur.execute("""UPDATE Users SET cash = %s
                    WHERE userID = %s """, (new_balance, session['userid']))
            conn.commit()
    conn.close()
    cur.close()
    return redirect(url_for('views.account'))


