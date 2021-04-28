import os
import sqlite3
import datetime

db_path = './db/database.db'

class sqlite_connection:
    def __init__(self, path):
        self.path = path
        
    def __enter__(self):
        try:
            #try to establish connection with the database and return the cursor
            self.conn = sqlite3.connect(db_path)
            return self.conn.cursor()
        except sqlite3.Error as e:
            #print out error
            print(e)

    def __exit__(self, type, value, traceback):
        if self.conn:
            #commit changes to database and close connection
            self.conn.commit()
            self.conn.close()

def init():
    # Create directory
    if not os.path.exists('./db'):
        os.mkdir('./db')

    # Initialize database
    with sqlite_connection(db_path) as cursor:
        
        # Create a table for storing all raw tweet data
        command = """
            CREATE TABLE IF NOT EXISTS tweets(
                id INT UNIQUE PRIMARY KEY,
                user_id INT NOT NULL,
                reply_to_id INT,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                place_country TEXT,
                favourite_count INT NOT NULL,
                retweet_count INT NOT NULL,
                UNIQUE(id) ON CONFLICT IGNORE
            );
        """
        cursor.execute(command)
        
        # Create a table for manually reviewed sentiment scores
        command = '''
        CREATE TABLE IF NOT EXISTS review_results(
            tweet_id INTEGER PRIMARY KEY UNIQUE,
            sentiment INT NOT NULL,
            relevancy INT NOT NULL,
            FOREIGN KEY (tweet_id)
                REFERENCES tweets (id)
            )'''
        cursor.execute(command)

def add_tweets(tweets):
    with sqlite_connection(db_path) as cursor:
        command = """
            INSERT INTO tweets(
                id,
                user_id,
                reply_to_id,
                text,
                created_at,
                place_country,
                favourite_count,
                retweet_count
            )
            VALUES (?,?,?,?,?,?,?,?)
        """
        # Wrap values into tuples
        values = map(lambda x: (
                    x.id,
                    x.user.id,
                    x.in_reply_to_status_id,
                    x.full_text,
                    x.created_at,
                    x.place.country_code if x.place else None,
                    x.favorite_count,
                    x.retweet_count),
                    tweets)
        cursor.executemany(command,values)

def get_latest_tweet_id():
    try:
        with sqlite_connection(db_path) as cursor:
            if cursor:
                command = """
                    SELECT MAX(id)
                    FROM tweets
                """
                cursor.execute(command)
                return cursor.fetchone()[0]
    except sqlite3.Error as err:
        print(f"Failed to retrieve latest tweet id: {err}")
        return None

def get_unreviewed_tweets():
    try:
        with sqlite_connection(db_path) as cursor:
            if cursor:
                command = """
                    SELECT id, text
                    FROM tweets
                    WHERE id NOT IN
                        (SELECT tweet_id 
                        FROM review_results)
                """
                cursor.execute(command)
                return cursor.fetchall()
    except:
        return None

init()