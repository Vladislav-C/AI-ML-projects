"""
  Steps:
    1) Data preparation
      Create a labeled dataset for supervised learning
    2) Feature extraction
      Transform text into numberical data
    3) Train split
      80% of data used for training
      20% used for testing
    4) Train model
      Teach the algorithm to recognize patterns in data
    5) Evaluate its performance
    6) Predict function
"""

import pickle
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report


NEWS_FILE = "bitcoin_news_train.txt"


# Data preparation
def load_BTC_articles(filename="bitcoin_news_train.txt"):
  with open(filename, 'r', encoding="utf-8") as file:
    content = file.read()

  articles = []
  for article in content.split('Article'):
    article = article.strip()

    if article:
      articles.append(article)

  return articles


# Data labelling
# Combined approach - pre-trained sentiment analysis tool + cypto specific words
def hybrid_labeling(articles):
  sid = SentimentIntensityAnalyzer()

  sid.lexicon.update({
    'bullish': 3.0, 'bearish': -3.0, 
    'mooning': 4.0, 'dumping': -4.0,
    'hodl': 1.5, 'fud': -2.5
  })

  labeled_data = []
  for article in articles:
    scores = sid.polarity_scores(article)

    if scores['compound'] >= 0.05:
      sentiment = 'positive'
    elif scores['compound'] <= -0.05:
      sentiment = 'negative'
    else:
      sentiment = 'neutral'
    
    labeled_data.append((article, sentiment))

  return labeled_data


articles = load_BTC_articles(NEWS_FILE)
labeled_data = hybrid_labeling(articles)

# Convert to DataFrame
df = pd.DataFrame(labeled_data, columns=["article", "sentiment"])



########### Model Training ###########

# Convert text data to feature vectors
vectorizer = CountVectorizer(max_features=3000)
X = vectorizer.fit_transform(df["article"])
y = df["sentiment"]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train a Naive Bayes classifier
model = MultinomialNB()
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
print(f"Classification Report:\n{classification_report(y_test, y_pred)}")

#########################################

with open("models/sentiment_model.pkl", "wb") as f:
  pickle.dump(model, f)

with open("models/vectorizer.pkl", "wb") as f:
  pickle.dump(vectorizer, f)

#########################################

