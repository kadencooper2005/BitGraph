import datetime as datime
import requests
import pandas as pd
import logging
import os
import time
from datetime import timezone

# Setup logging config
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG to see more details
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_timestamp(date):
    return int(date.timestamp())

def fetch_articles(params):
    response = requests.get(url, params=params)
    logging.info(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        logging.error(f"Error fetching articles: {response.status_code}")
        return None
        
    data = response.json()
    if not data.get("Data"):
        logging.info("No more articles found")
        return None
        
    article = []
    headers = ["PUBLISHED_ON", "TITLE", "URL"]

    for i in data["Data"]:
        # Convert Unix timestamp to human-readable date
        published_date = datime.datetime.fromtimestamp(i["PUBLISHED_ON"], timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        listing = [published_date, i["TITLE"], i["URL"]]
        article.append(listing)

    if article:
        df = pd.DataFrame(article, columns=headers)
        # Append to existing CSV if it exists, otherwise create new
        if os.path.exists("bitcoin_news.csv"):
            df.to_csv("bitcoin_news.csv", mode='a', header=False, index=False)
        else:
            df.to_csv("bitcoin_news.csv", index=False)
        logging.info(f"Added {len(article)} articles to bitcoin_news.csv")
        return True
    return None

# API request setup
url = "https://data-api.coindesk.com/news/v1/search"
base_params = {
    "search_string": "Bitcoin",
    "source_key": "coindesk",
    "api_key": "f33b582d4e2a6267324ecc5b3fdcbcc26097916fe629ea5c1ec42270f46c63ff",
    "limit": 100,
    "lang": "EN"
}

# Set up date range
start_date = datime.datetime(2014, 1, 1, tzinfo=timezone.utc)
end_date = datime.datetime.now(timezone.utc)
current_date = start_date

logging.info(f"Starting data collection from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

# Main loop to fetch all articles
while current_date <= end_date:
    # Set the end of the current period (3 months later)
    period_end = min(current_date + datime.timedelta(days=90), end_date)
    
    params = base_params.copy()
    params["to_ts"] = get_timestamp(period_end)
    params["from_ts"] = get_timestamp(current_date)
    
    logging.info(f"Fetching articles from {current_date.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}")
    
    if not fetch_articles(params):
        logging.info(f"No articles found for period {current_date.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}")
    
    # Move to next period
    current_date = period_end + datime.timedelta(days=1)
    
    # Add a small delay to avoid hitting rate limits
    time.sleep(1)

logging.info("Data collection completed!")

# Verify the last date in the CSV
if os.path.exists("bitcoin_news.csv"):
    df = pd.read_csv("bitcoin_news.csv")
    last_date = pd.to_datetime(df['PUBLISHED_ON'].iloc[-1])
    logging.info(f"Last article date in CSV: {last_date}")
