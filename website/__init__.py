from flask import Flask, render_template, request

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