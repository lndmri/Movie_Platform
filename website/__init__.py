from flask import Flask, render_template, request
import psycopg2, psycopg2.extras
from datetime import timedelta


# function to start the application
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '249234823423234sdkfsd-sdfjksndck'
    app.permanent_session_lifetime = timedelta(days=30)
    
    from .views import views
    from .auth import auth
    
    # registering blueprints so we can do routes
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app