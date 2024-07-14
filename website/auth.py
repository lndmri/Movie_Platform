from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2, psycopg2.extras
import re, logging
from flask_login import login_required, current_user, login_user, logout_user
from datetime import timedelta
from .helpers import db_conn_user, db_conn_admin

auth = Blueprint('auth',__name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    conn = db_conn_user()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password1 = request.form['password']

        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cur.fetchone()

        if account:
            password_rs = account['password_hash']
            if check_password_hash(password_rs, password1):
                session.permanent = True
                session['userid'] = account['userid']
                session['firstname'] = account['firstname']
                session['isadmin'] = account['isadmin']
                flash('Logged in successfully', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect email/password', category='error')
        else:
            flash('Incorrect email/password', category='error')
        conn.close()
        cur.close()
        return render_template("login.html", isLogin=True)
    else:
        if "userid" in session:
            return redirect(url_for('views.home'))
        return render_template("login.html", isLogin=True)


@auth.route('/details/logout')
@auth.route('/logout')
def logout():
    session.pop("userid", None)
    session.pop("isadmin", None)
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    conn = db_conn_user()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cur.fetchone()

        if account:
            flash('Email already exists.', category='error')
        elif not re.fullmatch(regex, email):
            flash('Email not valid', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 8 or len(password1) > 20:
            flash('Password must contain from 8 to 20 characters.', category='error')
        elif re.search('[0-9]',password1) is None:
            flash('Password must contain one number.', category='error')
        elif re.search('[a-z]',password1) is None: 
            flash('Password must contain a lower case letter.', category='error') 
        elif re.search('[A-Z]',password1) is None: 
            flash('Password must contain an upper case letter.', category='error') 
        elif re.search('[\+\.\\~`!@#:;"<,>/\$%\^&\*\(\)\{\}\[\]\?=_-]',password1) is None:
            flash('Password must contain a special character.', category='error')
        else:
            conn = db_conn_user()
            cur = conn.cursor()
            hashed_password = generate_password_hash(
                password1, method='pbkdf2:sha256')
            cur.execute('''INSERT INTO users (email, firstname, lastname, password_hash) VALUES (%s, %s, %s, %s)''',
                        (email, firstName, lastName, hashed_password))
            conn.commit()

            cur.execute('SELECT * FROM users WHERE email = %s', (email,))
            new_userID = cur.fetchone()
            user_id = new_userID[0]

            cur.execute("""INSERT INTO Transactions (userID, transactionType, amount, balanceBefore, balanceAfter)
                        VALUES (%s, %s, %s, %s, %s)""", (user_id, "Cash Bonus", 100, 0, 100,))
            conn.commit()

            cur.close()
            conn.close()
            flash('Account created!', category='success')
            return redirect(url_for('auth.login'))
        
    else:
        if "userid" in session:
            return redirect(url_for('views.home'))
        return render_template("sign_up.html", isSignUp=True)
    
    return render_template("sign_up.html", isSignUp=True)
