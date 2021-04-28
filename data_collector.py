from datetime import datetime, date, timedelta
import tweepy
import config
import db_manager

def build_query(search_terms):
    # Put terms into brackets
    terms = list(map(lambda x: f'({x})' , search_terms))
    # Join the terms with OR
    q = ' OR '.join(terms)
    # Filter retweets
    q += ' -filter:retweets'
    return q

def get_new_tweets(items=None, minus_days=None, wait_on_rate_limit=False):

    print("Initialising Twitter API client")
    # Initialise Twitter API
    auth = tweepy.OAuthHandler(config.api_key(), config.api_secret_key())
    auth.set_access_token(config.access_token(), config.access_token_secret())
    twitter_api = tweepy.API(auth, wait_on_rate_limit=wait_on_rate_limit, wait_on_rate_limit_notify=wait_on_rate_limit)

    print("Building request")

    # Define search terms
    search_keywords = [
        # Vaccine and its alias
        'covid vaccine', 'covax', 'COVID-19 Vaccine', 'anti covid vaccine'
        # Pfizer-BioNTech and its alias
        'Pfizer', 'BioNTech',
        # Oxford/AstraZeneca
        'Oxford', 'AstraZeneca',
        # Moderna
        'Moderna',
    ]

    query =  build_query(search_keywords)


    # Only get tweets in English
    lang = 'en'
    # Retrieve maximum number of tweets per request (default is 15)
    count = 100
    # Make sure retrieved tweets are in full text, default mode truncates text to 140 characters
    tweet_mode = 'extended'
    # Datetime of a specific date
    until = date.today() - timedelta(days=minus_days + 1) if (minus_days and minus_days > 0) else None
    # Prevent getting results before since_id which reduces the chance of getting replicated data. Should only be defined if until is None.
    since_id = db_manager.get_latest_tweet_id() if not until else None

    try:
        # Create an iterator to retrieve tweets
        tweets = tweepy.Cursor(twitter_api.search, q=query, lang=lang, since_id=since_id, until=until, count=count, tweet_mode=tweet_mode).items(items)

        print("filtering reponse from twitter")

        entries = list()
        for tweet in tweets:
            # Ignore quoted retweets
            if hasattr(tweet, 'retweeted_status'):
                continue
            # Add tweets in list
            entries.append(tweet)
    except Exception as err:
        print(f"Failed to retrieve tweets from twitter: {err}")
    
    print(f"adding {len(entries)} tweets to the database")
    # Save tweets into database
    db_manager.add_tweets(entries)

    print(f"Fetch data completed")