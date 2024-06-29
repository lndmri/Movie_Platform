from website import create_app

app = create_app()

if __name__ == '__main__': # only if we run the main file we are going to run the web server. We only run the web server if we run it from the main.py file
    app.run(debug=True)