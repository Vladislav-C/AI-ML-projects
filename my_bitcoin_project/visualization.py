"""Script to produce a line graph based on bitcoin prices stored in the DB"""

import logging
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#Set up logging config
logging.basicConfig(
  filename = "project.log",
  level = logging.INFO,
  format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger('data_visualization')


DB_PATH = "bitcoin.db"
GRAPH_FILE = "bitcoin_price.png"


def main():
  """Main function to draw graphs based on BTC data daily"""
  logger.info("Starting Bitcoin data visualization")

  BTC_data = get_BTC_data(days=90)
  if BTC_data == None:
    logger.error("Failed to get Bitcoin data. Exiting")
    return

  success = draw_price_graph(BTC_data)
  if success:
    logger.info("Bitcoin visualization completed successfully")
  else:
    logger.info("Failed to create Bitcoin price visualization")


def get_BTC_data(db_path=DB_PATH, days=90):
  """Conncet to DB and retrive data: array of (date, price)"""

  db = Path(db_path)

  try:
    if not db.exists():
      raise FileNotFoundError(f"Database not found at {db_path}")

    # Connect to DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if days > 0:
      # Calculate the start date based on specified days
      start_date  = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
      # Get price/date data for specified period
      cursor.execute("SELECT date, value FROM bitcoin_prices WHERE date >= ? ORDER BY date ASC", (start_date,))
    else:
      # Get all price/date data
      cursor.execute("SELECT date, value FROM bitcoin_prices ORDER BY date ASC")

    rows = cursor.fetchall()

    if not rows:
      logger.warning(f"No Bitcoin data found in DB for the specified period")
      return None

    logger.info(f"Successfully retrived {len(rows)} BTC price records from {db_path}")
    return rows

  except FileNotFoundError as e:
    logger.error(f"File path error: {e}")
    return None
  except sqlite3.Error as e:
    if conn:
      conn.rollback()
    logger.error(f"Database error: {e}")
    return None
  finally:
    if conn:
      conn.close()


def draw_price_graph(data, output_path=GRAPH_FILE, title="Bitcoin Price Over Time", color="red"):
  """Draws line graph of Bitcoin prices over time"""

  if not data:
    logger.warning("No data provided for visualization")
    return False
  try:
    dates, prices = [], []

    for date, price in data:
      dates.append(date)
      prices.append(price)

    # Creaet the plot
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots()
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

    # Plot the data
    ax.plot(dates, prices, color=color, linewidth=2, alpha=0.8)

    # Add data points
    ax.scatter(dates, prices, color=color, s=30, alpha=0.6)

    # Calculate simple moving average (7-day) if enough data points
    if len(dates) >= 7:
      sma = calculate_sma(prices, 7)
      ax.plot(dates[6:], sma, color='blue', linestyle='--', linewidth=1.5, alpha=0.7, label='7-Day SMA')
      ax.legend(loc='upper right')

    # Format plot
    ax.set_title(title, fontsize=24, pad=20)
    ax.set_xlabel('Date', fontsize=16, labelpad=10)
    fig.autofmt_xdate() # draws the date labels diagonally
    ax.set_ylabel('Price (USD)', fontsize=16, labelpad=10)
    ax.tick_params(labelsize=16)

    # Format x-axis dates
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close(fig)

    logger.info(f"Successfully created Bitoin price graph: {output_path}")
    return True

  except Exception as e:
    logger.error(f"Error creating graph: {e}")
    return False


def calculate_sma(prices, window):
  """Calculates simple moving average for the given price data"""

  if len(prices) < window:
    return[]
  
  sma_values = []
  for i in range(len(prices) - window + 1):
    window_average = sum(prices[i:i+window]) / window
    sma_values.append(window_average)
  
  return sma_values


main()