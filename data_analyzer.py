from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from analysis_model import VaderModel, TextBlobDefaultPA, TextBlobDefaultNBA, TextBlobNBC, SklearnNBMD, SklearnSVM

import db_manager
import os.path
import joblib
import re
import pandas as pd

trained_model_path = './trained_models'

def sentiment_analysis(retrain=False):

    models = []
    models_trained = False

    if not retrain:
        #Try to retrieve trained models
        trained_models = db_manager.get_analysis_models()
        if trained_models:
            models_trained = True
            for _, _, model_path in trained_models:
                try:
                    with open(f'{model_path}', 'rb') as f:
                        model = joblib.load(f)
                        models.append(model)
                except Exception as err:
                    print(f'Failed to load model: {err}')

    if not models:
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
        models_trained = False

    # Clear previous analysis history
    db_manager.clear_analysis_tables()
    
    # Split datasets
    x_train, x_test, y_train, y_test = get_dataset()

    # Train models
    if not models_trained:
        for model in models:
            print(f"Training model: {model.name}")
            model.train(x_train,y_train)
        
    # Classification
    for model in models:

        #Add or get model id
        model_id = db_manager.add_analysis_model(model.name)
        
        print(f"{model.name}: conducting classification")

        # Training data
        classify(model, x_train, y_train, 'train', model_id)

        # Testing data
        classify(model, x_test, y_test, 'test', model_id)

        # Save models
        if not models_trained:
            save_model(model, model_id)


def save_model(model, model_id):
    try:
        # Save model
        path = f'{trained_model_path}/{model.name}.joblib'
        print(f'{model.name}: Saving model at path {path}')

        # Check directory
        if not os.path.exists(trained_model_path):
            print(f'Trained model save directory not found ({trained_model_path}). Creating one.')
            os.mkdir(trained_model_path)
        
        with open(path, 'wb+') as f:
            joblib.dump(model, f)
        
        # Write to database
        db_manager.update_analysis_model_path(model_id, path)

    except Exception as err:
        print(f'Failed to save model: {err}')

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
    # Remove hyperlinks
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
