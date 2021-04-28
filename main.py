import data_collector
import tweet_reviews

def main():

    # Get all the data from the past 6 days
    for minus_days in range(7):
        data_collector.get_new_tweets(items=2000, minus_days=minus_days)
    
    
    # tweet_reviews.export('unreviewed.csv')
    pass

if  __name__ == "__main__":
    main()