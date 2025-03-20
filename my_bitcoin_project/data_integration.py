"""Script to retrieve and store Bitcoin price every day"""

import logging
import requests
import sqlite3
from datetime import datetime
from pathlib import Path

# Set up logging config
logging.basicConfig(
  filename = "project.log",
  level = logging.INFO,
  format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger('data_integration')


DB_PATH = "bitcoin.db"
COINDESK_API_URL = "https://data-api.coindesk.com/index/cc/v1/latest/tick"

def main():
  """Main function to run daily BTC price update"""
  logger.info("Starting Bitcoin price data integration")

  price = get_current_bitcoin_price()
  if price == None:
    logger.error("Failed to retrieve Bitcoin price. Exiting")
    return

  success = store_bitcoin_price(price)
  if success:
    logger.info("Bitcoin price data integration completed successfully")
  else:
    logger.error("Failed to store Bitcoin price data")


def get_current_bitcoin_price():
  """Retrieve the current Bitcoin price from CoinDesk API"""

  try:
    params = {
      "market": "ccix",
      "instruments": "BTC-USD"
    }

    response = requests.get(COINDESK_API_URL, params=params, timeout=10)
    response.raise_for_status()

    response_dict = response.json() # Convert the response object to a dict
    price = round(response_dict['Data']['BTC-USD']['VALUE'], 4)
    logger.info(f"Successfully retrieved BTC price: ${price}")
    return price

  except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching BTC price: {e}")
    return None
  except (KeyError, ValueError) as e:
    logger.error(f"Error parsing BTC price data: {e}")
    return None


def store_bitcoin_price(price, date=None, db_path=DB_PATH):
  """ Store Bitcoin price in SQLite DB"""

  if date == None:
    date = datetime.now().strftime("%Y-%m-%d")
  
  db = Path(db_path)

  try:
    if not db.exists():
      raise FileNotFoundError("Database cannot be found")

    # Connect to DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert or update price data
    cursor.execute("INSERT OR REPLACE INTO bitcoin_prices (date, value) VALUES (?, ?)", (date, price))

    conn.commit()
    logger.info(f"Successfully stored Bitcoin price for {date}")
    return True

  except FileNotFoundError as e:
    logger.error(f"File path error: {e}")
    return False
  except sqlite3.Error as e:
    if conn:
      conn.rollback()
    logger.error(f"Database error: {e}")
    return False
  finally:
    if conn:
      conn.close()


main()

"""
"Legacy DB population"

from pathlib import Path
import json
import sqlite3

path = Path('bit_year.json')
content = path.read_text()
bit_year_prices = json.loads(content)['bpi']

db_path = "my_bitcoin_project/bitcoin.db"

# Connect to the database
try:
  conn = sqlite3.connect(db_path)
except sqlite3.Error as e:
  print(f"Error connecting to database: {e}")
else:
  cursor = conn.cursor()

# Insert data into the table
for date, value in bit_year_prices.items():
  cursor.execute("INSERT INTO bitcoin_prices (date, value) VALUES (?, ?)", (date, value))

# Commite changes and close connection
conn.commit()
conn.close()
"""