import pickle

def load_BTC_articles(filename="bitcoin_news.txt"):
  with open(filename, 'r', encoding="utf-8") as file:
    content = file.read()

  articles = []
  for article in content.split('Article'):
    article = article.strip()

    if article:
      articles.append(article)

  return articles

def load_model(model_path="models/sentiment_model.pkl", vectorizer_path="models/vectorizer.pkl"):
  with open(model_path, "rb") as f:
    model = pickle.load(f)
  
  with open(vectorizer_path, "rb") as f:
    vectorizer = pickle.load(f)

  return model, vectorizer

def predict_crypto_sentiment(text, model, vectorizer):
  text_vector = vectorizer.transform([text])
  prediction = model.predict(text_vector)
  return prediction[0]


articles = load_BTC_articles()
model, vectorizer = load_model()

for article in articles:
  print(predict_crypto_sentiment(article, model, vectorizer))