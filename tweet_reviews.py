import db_manager
import pandas as pd
import os.path


def export(path):

    tweets = db_manager.get_unreviewed_tweets()

    if not tweets:

        print('No reviewed tweets available')

        return

    df = pd.DataFrame(tweets, columns=["id", "text"])

    df.to_csv(path, index=False, sep=',', encoding="utf-8")


def import_csv(path):
    
    # read the csv file from path
    df = pd.read_csv(path, dtype='str')

    # tweet id corrupted when export csv file (last 4 digits became 0s)
    # this part of code is to fix the id issue
    df_map = pd.read_csv('id_map.csv', dtype='str')
    df = pd.merge(df, df_map, on='id')
    df = df[['id_original','rate']]
    
    # filter unreviewed
    df = df.loc[df['rate'].notna()]

    # convert rate string into int
    
    def __rate_to_score(row):
        value = row['rate'].lower()
        if value == 'positive':
            return 1
        if value == 'neutral':
            return 0
        if value == 'negative':
            return -1
        return None

    df['score'] = df.apply(__rate_to_score, axis=1)

    values = map(lambda row: (row[1]['id_original'], row[1]['score']), df.iterrows())

    db_manager.add_manually_reviewed_tweets(values)


if __name__ == '__main__':
    import_csv('reviewed_data.csv')