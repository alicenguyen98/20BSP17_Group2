from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from analysis_model import VaderModel, TextBlobDefaultPA, TextBlobDefaultNBA, TextBlobNBC, SklearnNBMD, SklearnSVM

import db_manager
import re
import pandas as pd


def sentiment_analysis():
    db_manager.clear_analysis_tables()
    models = [
        VaderModel(),
        TextBlobDefaultPA(),
        TextBlobDefaultNBA(),
        TextBlobNBC(),
        SklearnNBMD(),
        SklearnNBMD(ngram_range=(1,2)),
        SklearnSVM(),
        SklearnSVM(ngram_range=(1,2))
    ]
    x_train, x_test, y_train, y_test = get_dataset()

    # Train models
    for model in models:
        print(f"Training model: {model.name}")
        model.train(x_train,y_train)
        
    # Classification
    for model in models:

        model_id = db_manager.add_analysis_model(model.name)
        
        print(f"{model.name}: conducting classification")

        # Training data
        classify(model, x_train, y_train, 'train', model_id)

        # Testing data
        classify(model, x_test, y_test, 'test', model_id)

def classify(model, x, y, label, model_id):
    # get classification
    classification = model.classify(x)
    # evaluate fitness
    report = classification_report(y, classification, output_dict=True)

    # Store results to database
    db_manager.add_classification(model_id, label, classification)
    db_manager.add_classification_performance(model_id, label, report['accuracy'], report['weighted avg']['precision'], report['weighted avg']['recall'], report['weighted avg']['f1-score'])

# Function to clean the tweets
def clean_text(tweet):
    # Remove @mentions
    tweet = re.sub(r'@[A-Za-z0-9]+', '',tweet)
    # Remove hashtags
    tweet = re.sub(r'#', '', tweet)
    # Remove RT
    tweet = re.sub(r'RT[\s]+', '', tweet)
    # Remove hyper links
    tweet = re.sub(r'https?:\/\/\S+', '',tweet)

    return tweet

def get_reviewed_tweets():
    # Fetch data from database
    review = db_manager.get_manually_reviewed_tweets()
    if not review:
        return 
    df = pd.DataFrame(review, columns=['id','text','sentiment']).set_index('id')
    # Remove irrelevant tweets
    df = df.dropna()
    return df

def get_dataset():
    df = get_reviewed_tweets()
    # Clean tweets
    df['text'] = df.apply(lambda x: clean_text(x['text']), axis = 1)
    # Split the data into training and testing data
    x_train, x_test, y_train, y_test = train_test_split(df['text'], df['sentiment'], train_size=0.5)
    return x_train, x_test, y_train, y_test
