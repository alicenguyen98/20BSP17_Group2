import os
import sqlite3
import datetime
import pandas as pd

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
                sentiment INT,
                FOREIGN KEY (tweet_id)
                    REFERENCES tweets (id)
            );
        '''
        cursor.execute(command)

        # Create analysis models table
        command = '''
        CREATE TABLE IF NOT EXISTS analysis_models(
            id INTEGER NOT NULL,
            name TEXT NOT NULL,
            path TEXT,
            PRIMARY KEY(id),
            UNIQUE(id)
            );'''
        cursor.execute(command)

        # Create analysis classification table
        command = '''
        CREATE TABLE IF NOT EXISTS analysis_classification(
            model_id INTEGER NOT NULL,
            label TEXT NOT NULL,
            tweet_id INTEGER NOT NULL,
            classification INTEGER NOT NULL,
            FOREIGN KEY (model_id)
                REFERENCES analysis_models (id),
            UNIQUE(model_id, label, tweet_id)
            );'''
        cursor.execute(command)

        # Create analysis performance table
        command = '''
        CREATE TABLE IF NOT EXISTS analysis_performance(
            model_id INTEGER NOT NULL,
            label TEXT NOT NULL,
            accuracy REAL NOT NULL,
            precision REAL NOT NULL,
            recall REAL NOT NULL,
            f1 REAL NOT NULL,
            FOREIGN KEY (model_id)
                REFERENCES analysis_models (id),
            UNIQUE(model_id, label)
            );'''
        cursor.execute(command)

#region raw data
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
                result = cursor.fetchone()
                return result[0] if result else None
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
#endregion
#region reviewed tweets
def add_manually_reviewed_tweets(tweets):
    try:
        with sqlite_connection(db_path) as cursor:
            if cursor:
                command = """
                    INSERT INTO review_results(
                        tweet_id,
                        sentiment
                    ) 
                    VALUES(?,?)
                    ON CONFLICT (tweet_id) DO UPDATE SET
                        sentiment=excluded.sentiment
                    """
                cursor.executemany(command, tweets)
    except sqlite3.Error as err:
        print(f"{err}")
        return None
def get_manually_reviewed_tweets():
    try:
        with sqlite_connection(db_path) as cursor:
            command = """
                SELECT review_results.tweet_id, tweets.text, review_results.sentiment
                FROM (tweets 
                INNER JOIN review_results ON tweets.id = review_results.tweet_id);
            """
            cursor.execute(command)
            return cursor.fetchall()
    except:
        return None
#endregion
#region analysed tweets
def clear_analysis_tables():
    with sqlite_connection(db_path) as cursor:
        command = """
            DELETE FROM analysis_models;
        """
        cursor.execute(command)

        command = """
            DELETE FROM analysis_classification;
        """
        cursor.execute(command)

        command = """
            DELETE FROM analysis_performance;
        """
        cursor.execute(command)

def get_analysis_models():
    try:
        with sqlite_connection(db_path) as cursor:
            command = """
                SELECT id, name, path
                FROM analysis_models
            """
            cursor.execute(command)
            return cursor.fetchall()
    except sqlite3.Error as err:
        print(err)
        return None

def get_analysis_model_name(id) -> str:
    try:
        with sqlite_connection(db_path) as cursor:
            command = """
                SELECT name
                FROM analysis_models
                WHERE id = ?;
            """
            cursor.execute(command, (id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as err:
        print(err)
        return None

def get_analysis_model_id(name) -> int:
    try:
        with sqlite_connection(db_path) as cursor:
            command = """
                SELECT id
                FROM analysis_models
                WHERE name = ?;
            """
            cursor.execute(command, (name,))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as err:
        print(err)
        return None

def add_analysis_model(name) -> int:
    try:
        with sqlite_connection(db_path) as cursor:
            command = """
                INSERT INTO analysis_models(name)
                    VALUES(?);
                """
            cursor.execute(command, (name,))

            command = """
                SELECT id
                FROM analysis_models
                WHERE name = ?;
            """
            cursor.execute(command, (name,))

            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as err:
        print(err)
        return None

def update_analysis_model_path(model_id, path):
        try:
            with sqlite_connection(db_path) as cursor:
                command = """
                    UPDATE analysis_models
                    SET path = ?
                    WHERE id = ?
                    """
                cursor.execute(command, (path, model_id))
        except sqlite3.Error as err:
            print(err)
            return None

def get_classification(model_id, label):
    try:
        with sqlite_connection(db_path) as cursor:
            command = f"""
                SELECT tweet_id, classification 
                FROM analysis_classification
                WHERE model_id = ? AND label = ?;
            """
            values = (model_id, label)
            cursor.execute(command, values)
            return cursor.fetchall()
    except sqlite3.Error as err:
        print(err)
        return None

def add_classification(model_id, label, classification: pd.Series):
    try:
        with sqlite_connection(db_path) as cursor:
            command = """
                INSERT INTO analysis_classification(model_id, label, tweet_id, classification)
                    VALUES(?,?,?,?);
                """
            values = map(lambda x: (model_id, label, x[0], x[1]), classification.iteritems())
            cursor.executemany(command, values)
    except sqlite3.Error as err:
        print(err)

def get_all_classification_performance():
    try:
        with sqlite_connection(db_path) as cursor:
            command = f"""
                SELECT model_id, label, accuracy, precision, recall, f1
                FROM analysis_performance
            """
            cursor.execute(command)
            return cursor.fetchall()
    except sqlite3.Error as err:
        print(err)
        return None

def get_classification_performance(model_id, label):
    try:
        with sqlite_connection(db_path) as cursor:
            command = f"""
                SELECT accuracy, precision, recall, f1
                FROM analysis_performance
                WHERE model_id = ? AND label = ?;
            """
            values = (model_id, label)
            cursor.execute(command, values)
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as err:
        print(err)
        return None

def add_classification_performance(model_id, label, accuracy, precision, recall, f1):
    try:
        with sqlite_connection(db_path) as cursor:
            command = """
                INSERT INTO analysis_performance(model_id, label, accuracy, precision, recall, f1)
                    VALUES(?,?,?,?,?,?);
                """
            values = (model_id, label, accuracy, precision, recall, f1)
            cursor.execute(command, values)
    except sqlite3.Error as err:
        print(err)
#endregion
init()