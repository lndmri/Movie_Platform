import psycopg2

#connection to DB
def db_conn():
    DB_HOST = "localhost"
    DB_NAME = "Movies_DB"
    DB_USER = "postgres"
    DB_PASS = "palm"

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    return conn