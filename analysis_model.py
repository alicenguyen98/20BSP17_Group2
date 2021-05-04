import pandas as pd
import vaderSentiment.vaderSentiment as vader

import textblob as tb
import textblob.sentiments
import textblob.classifiers

import sklearn as skl
import sklearn.feature_extraction.text
import sklearn.naive_bayes
import sklearn.svm


#region base classes
class BaseModel:
    """
    Skeleton of other models
    """
    def __init__(self, name):
        self.name = name

    def classify(self, x: pd.Series) -> pd.Series:
        raise NotImplementedError()

    def train(self, x: pd.Series, y: pd.Series):
        print("Training unavailable")

    @staticmethod
    def sentiment_score(x):
        if x >= 0.5:
            return 1
        elif x <= -0.5:
            return -1
        else:
            return 0

class TextBlobBaseModel(BaseModel):
    """
    Skeleton for TextBlob models
    """
    def classify(self, x: pd.Series) -> pd.Series:
        classification = x.apply(self._classify)
        return classification

    def _classify(self,x):
        raise NotImplementedError()

class SklearnBaseModel(BaseModel):
    """
    Skeleton for Sklearn models
    """
    def __init__(self, name, classifier, ngram_range=(1,1)):
        self._classifier = classifier
        self._vectorizer = skl.feature_extraction.text.TfidfVectorizer(ngram_range=ngram_range, stop_words=skl.feature_extraction.text.ENGLISH_STOP_WORDS)
        super().__init__(name)

    def classify(self, x: pd.Series) -> pd.Series:
        # Retrieve matrix from trained vectorizer
        matrix = self._vectorizer.transform(x)
        # Flatten the feature matrix into vector (single dimension)
        vector = matrix.toarray()
        # Make classifications
        classification = self._classifier.predict(vector)
        # Wrap result into pandas series
        return pd.Series(classification, index=x.index)

    def train(self, x: pd.Series, y: pd.Series):
        # Initialise feature vector
        self._vectorizer.fit(x)
        matrix = self._vectorizer.transform(x)
        # Flatten the feature matrix into vector (single dimension)
        vector = matrix.toarray()
        # Train the model
        self._classifier.fit(vector, y)
#endregion

#region vader class
class VaderModel(BaseModel):
    """
    This class is for VaderSentiment model
    classify text using SentimentIntensityAnalyzer - lexicon-based approach
    does not need to be trained
    """
    def __init__(self):
        self._analyzer = vader.SentimentIntensityAnalyzer()
        super().__init__('VaderMD')

    def classify(self, x: pd.Series) -> pd.Series:
        classification = x.apply(lambda x: BaseModel.sentiment_score(self._analyzer.polarity_scores(x)['compound']))
        return classification
 
#endregion

#region textblob classes
class TextBlobDefaultPA(TextBlobBaseModel):
    """
    This class use TextBlob default pattern analyzer
    """
    def __init__(self):
        self._analyzer = tb.sentiments.PatternAnalyzer()
        super().__init__('TextBlobPA')

    def _classify(self, x):
        sentiment = self._analyzer.analyze(x)
        return BaseModel.sentiment_score(sentiment.polarity)

class TextBlobDefaultNBA(TextBlobBaseModel):
    """
    This class use TextBlob default Naive Bayse Analyzer,
    the analyzer is trained with tb default corpus (NLTK movie review corpus)
    """
    def __init__(self):
        self._analyzer = tb.sentiments.NaiveBayesAnalyzer()
        super().__init__('TextBlobDefNBA')

    def train(self, x: pd.Series, y: pd.Series):
        self._analyzer.train()

    def _classify(self, x):
        sentiment = self._analyzer.analyze(x)
        if sentiment.p_pos > sentiment.p_neg:
            return 1
        if sentiment.p_pos < sentiment.p_neg:
            return -1
        return 0
    
class TextBlobNBC(TextBlobBaseModel):
    """
    This class use TextBlob Naive Bayse Classifier, 
    the model is trained with our own data
    """
    def __init__(self):
        super().__init__('TextBlobNBC')

    def train(self, x: pd.Series, y: pd.Series):
        df = pd.concat([x,y], axis=1)
        data = [x for x in df.itertuples(index=False)]
        self._classifier = tb.classifiers.NaiveBayesClassifier(data)
        self._classifier.train()
    
    def _classify(self, x):
        prob_dist = self._classifier.prob_classify(x)
        return prob_dist.max()

#endregion

#region self-built model
class SklearnNBMD(SklearnBaseModel):
    """
    This class use Sklearn library to build a Naive Bayse, Tfidf vectorizer sentiment analysis model,
    the model is trained with our own data
    """
    def __init__(self, ngram_range:tuple=(1,1)):
        classifier = skl.naive_bayes.GaussianNB()
        super().__init__(f'SklearnNB ngram={ngram_range}', classifier, ngram_range = ngram_range)
     
class SklearnSVM(SklearnBaseModel):
    """
    This class use Sklearn library to build a Support Vector Machine sentiment analysis model,
    the model is trained with our own data
    """
    def __init__(self, ngram_range:tuple=(1,1)):
        classifier = skl.svm.SVC()
        super().__init__(f'SklearnSVM ngran={ngram_range}', classifier, ngram_range = ngram_range)
#endregion