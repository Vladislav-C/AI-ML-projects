"""Script to fetch and temperary store the latest news"""

import logging
import requests

# Set up logging config
logging.basicConfig(
  filename = "project.log",
  level = logging.INFO,
  format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger('news_analysis')


COINDESK_API_URL = "https://data-api.coindesk.com/news/v1/article/list"
NEWS_FILE = "bitcoin_news.txt"


def main():
  """Main function to retrieve and store news"""

  logger.info("Starting Bitcoin news analysis")
  
  news_articles = get_news_about_bitcoin()
  if news_articles == None:
    logger.error("Failed to retrieve Bitcoin news. Exiting.")
    return

  text_save_success = save_new_to_text(news_articles)

  if text_save_success:
    logger.info("Bitcoin news analysis and storage completed successfully")
  else:
    logger.warning("Bitoin news analysis completed with some issues")


def get_news_about_bitcoin(limit=3, lang="EN"):
  """Retrieves current news from CoinDesk API"""
  try:
    params = {
      "lang": lang,
      "limit": limit
    }

    logger.info(f"Fetching {limit} Bitcoin news articles in {lang}")
    response = requests.get(COINDESK_API_URL, params=params, timeout=10)
    response.raise_for_status()

    response_dict = response.json()
    news_articles = response_dict['Data']
    logger.info(f"Successfully retrieved {len(news_articles)} news about BTC")
    return news_articles

  except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching news on BTC: {e}")
    return None
  except (KeyError, ValueError) as e:
    logger.error(f"Error parsing news about BTC: {e}")
    return None


def save_new_to_text(news_articles, output_file=NEWS_FILE):
  """Saves articles in txt format into text file"""

  if not news_articles:
    logger.warning("No news articles to save")
    return False

  try:
    with open(output_file, "w", encoding="utf-8") as file:
      for i, article in enumerate(news_articles, 1):
        title = article['TITLE']
        body = article['BODY']

        file.write(f"Article {i}: {title}\n")
        file.write(f"Content:\n")
        file.write(f"{body}\n")

    logger.info(f"Successfully saved {len(news_articles)} news articles to {output_file}")
    return True

  except IOError as e:
    logger.error(f"Error saving news to text file: {e}")
    return False


main()