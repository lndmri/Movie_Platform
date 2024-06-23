from flask import Flask, render_template, request
import psycopg2, psycopg2.extras

#create connector to DB 
DB_HOST = "localhost"
DB_NAME = "Movies_DB"
DB_USER = "postgres"
DB_PASS = "database24"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                        password=DB_PASS, host=DB_HOST)

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cur.execute('''CREATE TABLE IF NOT EXISTS users(email VARCHAR (50) PRIMARY KEY, firstname varchar(1024), password1 VARCHAR(1024));''')
conn.commit()
cur.close()
conn.close()

# function to start the application
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '249234823423234sdkfsd-sdfjksndck'
    
    from .views import views
    from .auth import auth
    
    # registering blueprints so we can do routes
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app