#!/usr/bin/env python3

import string
import pickle
import sqlite3
import argparse
import warnings

from nltk import pos_tag
from nltk import sent_tokenize
from nltk import WordNetLemmatizer
from nltk import wordpunct_tokenize
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords as sw

from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split as tts


DESCRIPTION = "Model commands and application for the reviews app"
EPILOG      = "If there are any bugs or concerns, submit an issue on Github"
VERSION     = "%(prog)s v1.0.0"

warnings.filterwarnings('ignore')


class NLTKPreprocessor(BaseEstimator, TransformerMixin):

    def __init__(self, stopwords=None, punct=None, lower=True, strip=True):
        self.stopwords = stopwords or set(sw.words('english'))
        self.lower = lower
        self.strip = strip
        self.punct = punct or set(string.punctuation)
        self.lemmatizer = WordNetLemmatizer()

    def fit(self, X, y=None):
        return self

    def inverse_transform(self, X):
        return [" ".join(doc) for doc in X]

    def transform(self, X):
        return [
            list(self.tokenize(doc)) for doc in X
        ]

    def tokenize(self, document):
        # Break the document into sentences
        for sent in sent_tokenize(document):
            # Break the sentence into part of speech tagged tokens
            for token, tag in pos_tag(wordpunct_tokenize(sent)):
                # Apply preprocessing to the token
                token = token.lower() if self.lower else token
                token = token.strip() if self.strip else token
                token = token.strip('_') if self.strip else token
                token = token.strip('*') if self.strip else token

                # If stopword, ignore token and continue
                if token in self.stopwords:
                    continue

                # If punctuation, ignore token and continue
                # TODO: this will get rid of ASCII emoji
                if all(char in self.punct for char in token):
                    continue

                # If starts with @ remove to prevent leakage
                if token.startswith("@"):
                    continue

                # Lemmatize the token and yield
                lemma = self.lemmatize(token, tag)
                yield lemma

    def lemmatize(self, token, tag):
        tag = {
            'N': wn.NOUN,
            'V': wn.VERB,
            'R': wn.ADV,
            'J': wn.ADJ
        }.get(tag[0], wn.NOUN)

        return self.lemmatizer.lemmatize(token, tag)


relabel = {
    "negative": "NEG",
    "neutral": "NEU",
    "positive": "POS",
}

def identity(arg):
    """
    Simple identity function works as a passthrough.
    """
    return arg


def train(args):
    # Load dataset into memory (probably a bad idea)
    conn = sqlite3.connect(args.data)
    cur = conn.cursor()
    cur.execute("SELECT airline_sentiment, text FROM Tweets")
    corpus = cur.fetchall()
    cur.close()

    X = [row[1] for row in corpus]
    y = list(map(lambda row: relabel[row[0]], corpus))

    model = Pipeline([
        ("nltk", NLTKPreprocessor()),
        ("vec", TfidfVectorizer(
            tokenizer=identity, preprocessor=None, lowercase=False,
        )),
        ("maxent", LogisticRegression(
            penalty='l1', fit_intercept=True, solver='liblinear', max_iter=10000,
            multi_class='ovr', verbose=0, warm_start=False,
        )),
    ])

    X_train, X_test, y_train, y_test = tts(X, y, test_size=0.2, shuffle=True)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    model.fit(X, y)
    with open(args.out, "wb") as f:
        pickle.dump(model, f)


def predict(args):
    with open(args.model, 'rb') as f:
        model = pickle.load(f)

    print(model.predict(args.text))
    print(model.decision_function(args.text))


if __name__ == "__main__":
    cmds = [
        {
            "name": "train",
            "help": "train a sentiment model from tweets",
            "func": train,
            "args": {
                ("-d", "--data"): {
                    "type": str, "default": "fixtures/corpus.sqlite", "metavar": "PATH",
                    "help": "the path to the training data sqlite3 database",
                },
                ("-o", "--out"): {
                    "type": str, "default": "fixtures/model.pickle",
                    "metavar": "PATH", "help": "location to write model to disk",
                },
            },
        },
        {
            "name": "predict",
            "help": "make a prediction using the trained sentiment model",
            "func": predict,
            "args": {
                ("-m", "--model"): {
                    "type": str, "default": "fixtures/model.pickle", "metavar": "PATH",
                    "help": "the path to the model pickle file",
                },
                ("text",): {
                    "nargs": "+",
                    "help": "specify the text to make a polarity prediction on",
                },
            },
        }
    ]

    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG)
    parser.add_argument('-v', '--version', action="version", version=VERSION)
    subparsers = parser.add_subparsers(help="subcommands")

    for cmd in cmds:
        subparser = subparsers.add_parser(cmd['name'], help=cmd['help'])
        subparser.set_defaults(func=cmd['func'])

        for pargs, kwargs in cmd['args'].items():
            if isinstance(pargs, str):
                pargs = (pargs,)
            subparser.add_argument(*pargs, **kwargs)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        parser.error(str(e))