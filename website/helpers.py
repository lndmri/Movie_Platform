import psycopg2

#connection to DB for regular users
def db_conn_user():
    DB_HOST = "localhost"
    DB_NAME = "Movies_DB"
    DB_USER = "appuser"
    DB_PASS = "Lamarca@2024"

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    return conn

#connection to DB for admin user
def db_conn_admin():
    DB_HOST = "localhost"
    DB_NAME = "Movies_DB"
    DB_USER = "appadmin"
    DB_PASS = "Unalocura@2024"

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    return conn


def check_movie_exists(title, type, release_year):
     
    value = False
    try:
        # db connection
        conn = db_conn_admin()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # checking if the movie already exists in the DB
        cur.execute("SELECT movieID FROM Movies WHERE title = %s AND type = %s AND released = %s", (title, type, release_year))
        if cur.fetchone():
            value = True
                    
    except Exception as e:
        conn.rollback()
        message = str(e)
        print(message)

    finally:
        cur.close()
        conn.close()  
        return value


def add_movie_to_db(title, movie_type, price, duration, release_year, rating, score, genres, actors, directors, description):

    try:
        # db connection
        conn = db_conn_admin()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Insert data into Movies table
        cur.execute("""
            INSERT INTO Movies (title, price, type, duration, released, score, rating, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING movieID;
        """, (title, price, movie_type, duration, release_year, score, rating, description,))
        movie_result = cur.fetchone()

        if movie_result:
            movie_id = movie_result[0]
        else:
            print("NONE movie")

        # Inserting into Genres and ListedIn Tables
        for genre in genres:
            # Adding the Genre if the Genre is not in Listed in Genres Table
            cur.execute("""
                INSERT INTO Genres (name)
                VALUES (%s)
                ON CONFLICT ON CONSTRAINT name_g DO NOTHING
                RETURNING genreID;
            """, (genre,))
                
            genre_result = cur.fetchone()
            print(genre_result)

            # getting the genre_id
            # if the genre comes from the previous query
            if genre_result:
                genre_id = genre_result[0]
            else:
            # if the genre was ON CONFLICT
                cur.execute("SELECT genreID FROM Genres WHERE name = %s",(genre,))
                genre_result = cur.fetchone()
                print("QUERY SELECT RESULT:" + str(genre_result))
                if genre_result:
                        genre_id = genre_result[0]
                        
            #  Inserting the genre_id with its respective movie_id if the combination does not exist in the ListedIn table 
            if genre_id and movie_id:
                cur.execute("""
                    INSERT INTO ListedIn (movieID, genreID)
                    VALUES (%s, %s)
                    ON CONFLICT ON CONSTRAINT listedInPK DO NOTHING;
                """, (movie_id, genre_id))

        # Insert data into Actors and Works tables
        for actor in actors:

            # Adding the Actor if the Actor is not in listed in Actors Table
            cur.execute("""
                INSERT INTO Actors (name)
                VALUES (%s)
                ON CONFLICT ON CONSTRAINT name_a DO NOTHING
                RETURNING actorID;
            """, (actor,))
            
            actor_result = cur.fetchone()
            print(actor_result)

            # getting the actor_ID
            # if the actor comes from the previous query
            if actor_result:
                actor_id = actor_result[0]
            # if the actor was ON CONFLICT
            else:
                cur.execute("SELECT actorID FROM Actors WHERE name = %s",(actor,))
                actor_result = cur.fetchone()
                print("QUERY SELECT RESULT:" + str(actor_result))
                if actor_result:
                    actor_id = actor_result[0]

            #  Inserting the actor_id with its respective movie_id if the combination does not exist in the Works table 
            if actor_id and movie_id:
                cur.execute("""
                    INSERT INTO Works (movieID, actorID)
                    VALUES (%s, %s)
                    ON CONFLICT ON CONSTRAINT worksPK DO NOTHING;
                """, (movie_id, actor_id))

        # Insert data into Directors and Directs tables
        for director in directors:
            # Adding the Director if the Director is not in listed in Directors Table
            cur.execute("""
                INSERT INTO Directors (name)
                VALUES (%s)
                ON CONFLICT ON CONSTRAINT name_d DO NOTHING
                RETURNING dirID;
            """, (director,))
            
            dir_result = cur.fetchone()
            print(dir_result)

            # getting the dir_id
            # if the director comes from the previous query
            if dir_result:
                dir_id = dir_result[0]
            else:
            # if the director was ON CONFLICT
                cur.execute("SELECT dirID FROM Directors WHERE name = %s",(director,))
                dir_result = cur.fetchone()
                print("QUERY SELECT RESULT:" + str(dir_result))
                if dir_result:
                    dir_id = dir_result[0]

            #  Inserting the dir_id with its respective movie_id if the combination does not exist in the Works table 
            if dir_id and movie_id:                    
                cur.execute("""
                    INSERT INTO Directs (movieID, dirID)
                    VALUES (%s, %s)
                    ON CONFLICT ON CONSTRAINT directsPK DO NOTHING;
                """, (movie_id, dir_id))

        # Commit the transaction
        conn.commit()
        print("Movie Added Successfully")
        value = True
            
    except Exception as e:
        conn.rollback()
        message = str(e)
        print(message)
        value = False


    finally:
        cur.close()
        conn.close() 
        return value 
    


def upadate_movie_in_db(movieID, title, movie_type, price, duration, release_year, rating, score, genres, actors, directors, description):

    try:
        # db connection
        conn = db_conn_admin()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
         # Update movie details
        cur.execute("""UPDATE Movies
                        SET title = %s, type = %s, price = %s, duration = %s, released = %s, rating = %s, score = %s, description = %s
                        WHERE movieID = %s""",
                    (title, movie_type, price, duration, release_year, rating, score, description, movieID))

        # Remove existing  genres, actors, and directors from ListedIn, Works and Directs Tables
        if genres:
            cur.execute("DELETE FROM Listedin WHERE movieID = %s", (movieID,))
        if actors:
            cur.execute("DELETE FROM Works WHERE movieID = %s", (movieID,))
        if directors:
            cur.execute("DELETE FROM Directs WHERE movieID = %s", (movieID,))

        # Insert new genres, actors, and directors
        # Working in Genre

        if genres:
            for genre in genres:
                if genre == '':
                    continue
                # check if genre already exists in Genres table
                cur.execute("SELECT genreID FROM Genres WHERE name = %s",(genre, ))
                genre_result = cur.fetchone()
                
                # if the Genra is not listed in the Genres Tables we then insert it in the Genres table
                if not genre_result:
                    cur.execute("INSERT INTO Genres (name) VALUES (%s) RETURNING genreID", (genre, ))
                    genre_result = cur.fetchone()
                
                #  finally we add an entry to the ListedIn table
                if genre_result:
                    genre_id = genre_result[0]
                    cur.execute("INSERT INTO ListedIn (movieID, genreID) VALUES (%s, %s)", (movieID, genre_id))

        if actors:    
            for actor in actors:
                if actor == '':
                    continue
                # check if actor already exists in actors table
                cur.execute("SELECT actorID FROM Actors WHERE name = %s",(actor, ))
                actor_result = cur.fetchone()
                
                # if the Actor is not listed in the Actors Tables we then insert it in the Actors table
                if not actor_result:
                    cur.execute("INSERT INTO Actors (name) VALUES (%s) RETURNING actorID", (actor, ))
                    actor_result = cur.fetchone()
                
                #  finally we add an entry to the Works table
                if actor_result:
                    actorID = actor_result[0]
                    cur.execute("INSERT INTO Works (movieID, actorID) VALUES (%s, %s)", (movieID, actorID))

        for director in directors:
            if director == '':
                continue

            # check if director already exists in Directors table
            cur.execute("SELECT dirID FROM Directors WHERE name = %s",(director, ))
            director_result = cur.fetchone()
            
            # if the director is not listed in the Directors Tables we then insert it in the Directors table
            if not director_result:
                cur.execute("INSERT INTO Directors (name) VALUES (%s) RETURNING dirID", (director, ))
                director_result = cur.fetchone()
            
            #  finally we add an entry to the Directs table
            if director_result:
                directorID = director_result[0]
                cur.execute("INSERT INTO Directs (movieID, dirID) VALUES (%s, %s)", (movieID, directorID))

                conn.commit()
        print("Movie Updated Successfully")
        value = True
            
    except Exception as e:
        conn.rollback()
        message = str(e)
        print(message)
        value = False


    finally:
        cur.close()
        conn.close() 
        return value 