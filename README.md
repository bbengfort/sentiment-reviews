# Sentiment Reviews

**Code for the MLOps 201: Real Time Inferencing Webinar**

## Quickstart

To run the code locally on your computer, first make sure that [Docker and Docker Compose are installed](https://docs.docker.com/compose/install/). Then run the following commands from the root of the repository that you've cloned to your computer:

```
$ docker compose build
$ docker compose up
```

You should now be able to navigate to http://localhost:8000/ and see the app running.

## Sentiment Model

The model was trained on the [Kaggle Twitter US Airline Sentiment](https://www.kaggle.com/datasets/crowdflower/twitter-airline-sentiment?resource=download) dataset. The confusion matrix for the model is below:

```
precision    recall  f1-score   support

         NEG       0.81      0.93      0.86      1818
         NEU       0.64      0.47      0.54       620
         POS       0.77      0.60      0.68       459

    accuracy                           0.78      2897
   macro avg       0.74      0.67      0.70      2897
weighted avg       0.77      0.78      0.77      2897
```

The model uses an NLTK preprocessor that removes english stopwords and punctuation, lower casess and lemmatizes all words using the WordNet lemmatizer. A scikit-learn TFIDF vectorizer is used to vectorize the unigrams for the model. Finally a Logistic Regression (maximum entropy) model is used for classification.

The model can be found in [fixtures/model.pickle](fixtures/model.pickle) and you can use it to make predictions as follows:

```
$ ./models.py predict "I hate waiting in line, this is absolutely horrid"
['NEG']
[[ 3.2809592  -3.56670859 -2.75509941]]
```

The first row is the classification and the second row is the confidence the model has in the 'NEG', 'NEU', and 'POS' classes respectively.