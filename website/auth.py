from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2, psycopg2.extras
import re, logging
from flask_login import login_required, current_user, login_user, logout_user


auth = Blueprint('auth',__name__)

DB_HOST = "localhost"
DB_NAME = "Movies_DB"
DB_USER = "postgres"
DB_PASS = "database24"

#connection to DB
def db_conn():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    return conn

@auth.route('/login', methods=['GET', 'POST'])
def login():
    conn = db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password1 = request.form['password']

        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cur.fetchone()

        if account:
            password_rs = account['password1']
            if check_password_hash(password_rs, password1):
                session['loggedin'] = True
                session['email'] = account['email']
                flash('Logged in successfully', category='success')
                return redirect(url_for('views.account'))
            else:
                flash('Incorrect email/password', category='error')
        else:
            flash('Incorrect email/password', category='error')

    conn.close()
    cur.close()
    return render_template("login.html", isLogin=True)



@auth.route('/logout')
def logout():
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    conn = db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cur.fetchone()

        if account:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            conn = db_conn()
            cur = conn.cursor()
            hashed_password = generate_password_hash(
                password1, method='pbkdf2:sha256')
            cur.execute('''INSERT INTO users (email, firstname, password1) VALUES (%s, %s, %s)''',
                        (email, firstName, hashed_password))
            conn.commit()
            cur.close()
            conn.close()
            flash('Account created!', category='success')
            return redirect(url_for('auth.login'))

    return render_template("sign_up.html", isSignUp=True)