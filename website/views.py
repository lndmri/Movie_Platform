from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from flask_login import login_required, current_user
from .helpers import db_conn, check_movie_exists, add_movie_to_db
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

        # We get to this return statement if the user is logged in already
        return render_template('home.html', firstname=firstname)
    else:
        return redirect(url_for('auth.login'))

# Route for movie searching (this is a route only as we will be showing the content in the home page)

@views.route('/search', methods=["POST", "GET"])
def search():
    if "userid" in session:
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

    else:
        return redirect(url_for('auth.login'))


@views.route('/favorites', methods=["GET"])
def favorites():
    if "userid" in session:
        conn = db_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("""SELECT m.* FROM Movies m, Favorites f
                                WHERE m.movieID = f.movieID
                                AND userID = %s
                                ORDER BY f.time""", (session['userid'],))

        favorites = cur.fetchall()
        conn.close()
        cur.close()
        return render_template('favorites.html', favorites=favorites)

    else:
        return redirect(url_for('auth.login'))
    

@views.route('/buy_movie', methods=["POST"])
def buy_movie():

    if "userid" in session:
        try:
            # db connection
            conn = db_conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            if 'movieID' in request.form and 'title' in request.form and 'price' in request.form:
                movieID = request.form['movieID']
                title = request.form['title']
                price = float(request.form['price'])
            else:
                message = "Internal error"
                cur.close()
                conn.close()
                return jsonify({'message': message, 'status':'error'})

            # checking if the user has already bought that movie
            cur.execute("SELECT * FROM Owns WHERE userID = %s AND movieID = %s", (session['userid'], movieID))
            if cur.rowcount > 0:
                message = "You have already purchased this movie"   
                cur.close()
                conn.close()
                return jsonify({'message': message, 'status': 'error'})             
            else:
                # if the user has not purchased the movie before 
                # we check if the user has enough money
                cur.execute("SELECT cash FROM Users WHERE userID = %s", (session['userid'],))
                cash_result = cur.fetchone()
                # checking if we got a result from the query
                if cash_result:
                    cash = float(cash_result['cash'])
                    print(cash)
                else:
                    message = "Purchase successfully completed. To see your purchased movies go to 'My Movies'"
                    cur.close()
                    conn.close()
                    return jsonify({'message': message, 'status': 'success'})
 
                if cash < price:
                    message = "Insufficient funds to complete transaction.\n Plase add money to the account"
                    cur.close()
                    conn.close()
                    return jsonify({'message': message, 'status': 'error'})
                    
                else:
                    new_cash =  cash - price
                    cur.execute("UPDATE Users SET cash = %s WHERE userID = %s", (new_cash, session['userid'],))
                    cur.execute("INSERT INTO Owns (userID, movieID) VALUES (%s, %s)",(session['userid'], movieID,))
                    cur.execute("""INSERT INTO Transactions 
                                (userID, transactionType, movie, amount, balanceBefore, balanceAfter)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                """, (session['userid'], "Purchase", title, price, cash, new_cash,))
                    conn.commit()
                    message = "Purchase successfully completed.\n To see your purchased movies go to 'My Movies'"
                    return jsonify({'message': message, 'status': 'success'})

        except Exception as e:
            conn.rollback()
            message = str(e)
            print(message)
            return jsonify({'message': message, 'status': 'error'})
        finally:
            cur.close()
            conn.close()    
    else:
        return redirect(url_for('auth.login'))
    

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
        return render_template('my_movies.html', paid_movies=paid_movies)
    
    else:
        return redirect(url_for('auth.login'))
    

@views.route('/history')
def history():
    if "userid" in session:
        conn = db_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("SELECT * FROM Transactions WHERE userID = %s ORDER BY transaction_time DESC", (session['userid'],))
        transactions = cur.fetchall()
        conn.close()
        cur.close()
        return render_template('history.html', transactions=transactions)
    else:
        return redirect(url_for('auth.login'))


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
        cur.close()
        conn.close()
        return render_template('details.html', movie=movie, directors=directors, actors=actors)

    else:
        return redirect(url_for('auth.login'))


@views.route('/add_to_favorites', methods=['POST'])
def add_to_favorites():
    if "userid" in session:
        userId = session['userid']
        movieId = request.form.get('movieid')

        conn = db_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("SELECT * FROM Favorites WHERE userID = %s AND movieID = %s", (session['userid'], movieId))
        if cur.rowcount > 0:
            message = "You have already added this movie to Favorites"   
            cur.close()
            conn.close()
            return jsonify({'message': message, 'status': 'error'})  

        else: 
            cur.execute(
                "INSERT INTO favorites (userid, movieid) VALUES (%s, %s)", (userId, movieId))
            conn.commit()
            message = 'Movie added to Favorites!'
            cur.close()
            conn.close()
            return jsonify({'message': message})
    
    else:
        return redirect(url_for('auth.login'))  


@views.route('/remove_favorite', methods=["POST"])
def remove_favorite():
    if "userid" in session:
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
    
    else:
        return redirect(url_for('auth.login'))


@views.route('/account', methods=["GET"])
def account():
    if "userid" in session:
        conn = db_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("""SELECT * FROM Users
                        WHERE userID = %s """, (session['userid'],))
        results = cur.fetchone()
        conn.close()
        cur.close()
        return render_template('account.html', results=results)
    
    else:
        return redirect(url_for('auth.login'))

@views.route('/add_cash', methods=['GET', 'POST'])
def add_cash():
    if "userid" in session:
        conn = db_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cur.execute("""SELECT * FROM Users
                    WHERE userID = %s """, (session['userid'],))
        
        user = cur.fetchone()
        conn.close()
        cur.close()      
        return render_template('add_cash.html', user=user )

    else:
        return redirect(url_for('auth.login'))
    

@views.route('/update_cash', methods=['GET','POST'])
def update_cash():
    if "userid" in session:
        try:
            # db connection
            conn = db_conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            if 'amount' in request.form:
                amount = float(request.form['amount'])
                               
            else:
                message = "Internal error"
                cur.close()
                conn.close()
                return jsonify({'message': message, 'status':'error'})    

            cur.execute("""SELECT cash FROM Users WHERE userID = %s""", (session['userid'],))
            old_balance = cur.fetchone()
            cash = float(old_balance['cash'])

            new_balance =  cash + amount
            cur.execute("""UPDATE Users SET cash = %s WHERE userID = %s """, (new_balance, session['userid'],))
            cur.execute("""INSERT INTO Transactions 
                        (userID, transactionType, amount, balanceBefore, balanceAfter)
                        VALUES (%s, %s, %s, %s, %s)
                        """, (session['userid'], "Add cash", amount, cash, new_balance,))
            conn.commit()
            message = "Transaction successfully completed.\n To check your new balance go to 'Account'"
            conn.close()
            cur.close()
            return jsonify({'message': message, 'status': 'success'})
            

        except Exception as e:
            conn.rollback()
            message = str(e)
            print(message)
            return jsonify({'message': message, 'status': 'error'})

        finally:
            cur.close()
            conn.close()  

    else:
        return redirect(url_for('auth.login'))
    
# admin functions and routes:
@views.route('/add-movie', methods=['GET', 'POST'])
def add_movie():
    if "userid" in session:

        ratings = ["TV-Y","TV-Y7-FV","TV-G","TV-14","TV-MA","TV-Y7","G","NC-17","PG","TV-PG","PG-13","R","A","UR","NR"]

        if request.method == 'POST':
            title = request.form['title']
            movie_type = request.form['type']
            price = request.form['price']
            duration = request.form['duration']
            release_year = request.form['release_year']
            rating = request.form['rating']
            score = request.form['score']
            genres = request.form.getlist('genres')
            actors = request.form.getlist('actors')
            directors = request.form.getlist('directors')
            description = request.form['description']

            print(title)
            print(movie_type)
            print(price)
            print(duration)
            print(release_year)
            print(rating)
            print(score)
            print(genres)
            print(actors)
            print(directors)
            print(description)

        
            try:                
                # formatting duration of the movie/show
                if movie_type == 'Movie':
                    duration = str(duration) + " min"
                elif movie_type == 'TV Show':
                    if duration == 1:
                        duration = str(duration) + " season"
                    else:
                        duration = str(duration) + " seasons"
                else:
                    flash("Error processing duration.", "error")
                    return render_template("add_movie.html", ratings=ratings)
                
                # checking if the movie already exists in the DB
                if check_movie_exists(title, type, release_year):
                    flash("Movie already exists. If you need to change it please go to Home and update it", "error")
                    return render_template("add_movie.html", ratings=ratings)
                # if it is not in the DB we are going to add it to the DB
                else:
                    if add_movie_to_db(title, movie_type, price, duration, release_year, rating, score, genres, actors, directors, description):
                        flash("Movie successfully added to the database", 'success')
                        return render_template("add_movie.html", ratings=ratings)

            except Exception as e:
                flash("Error", "error")
                print(e)   
                return render_template("add_movie.html", ratings=ratings)
            
        
        else:       
            return render_template("add_movie.html", ratings=ratings)
        
    else:
        return redirect(url_for('auth.login'))
        



