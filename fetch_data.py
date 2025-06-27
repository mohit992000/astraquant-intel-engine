import yfinance as yf
import pandas as pd 
import time
import logging
import os
import subprocess
from datetime import datetime, timezone
import pytz

# Settings
tickers = ["SPY", "NQ=F", "BTC-USD"]
interval = "1m"
delay_seconds = 60  # How often to fetch new bar

# Setup logging
logging.basicConfig(filename="live_fetch.log", level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def fetch_latest_bar(ticker):
    utc_now = datetime.now(timezone.utc)
    print(f"\n🕒 Fetching latest bar for {ticker} at {utc_now.strftime('%Y-%m-%d %H:%M:%S')} UTC...")
    logging.info(f"Fetching latest bar for {ticker} at {utc_now}")

    data = yf.download(
        ticker,
        period="2m",  # Fetch last 2 minutes to ensure coverage
        interval=interval,
        progress=False,
        auto_adjust=False  # Prevent FutureWarning
    )

    if data.empty:
        print(f"❌ No recent data for {ticker}")
        logging.warning(f"No data fetched for {ticker}")
        return None

    latest = data.iloc[-1:].copy()
    latest = latest[['Close', 'Volume']].dropna()
    latest = latest.rename(columns={'Close': 'price', 'Volume': 'volume'})
    latest.reset_index(inplace=True)
    latest.rename(columns={'Datetime': 'timestamp'}, inplace=True)

    # Convert UTC to EST
    latest['timestamp'] = latest['timestamp'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')

    # Sanity checks
    if 'price' in latest.columns and 'volume' in latest.columns:
        latest['price'] = pd.to_numeric(latest['price'], errors='coerce')
        latest['volume'] = pd.to_numeric(latest['volume'], errors='coerce')
        latest.dropna(subset=['price', 'volume'], inplace=True)
        return latest
    else:
        print("⚠️ Missing expected columns.")
        return None

def append_if_new(filename, new_row):
    if os.path.exists(filename):
        existing = pd.read_csv(filename)
        if 'timestamp' in existing.columns:
            existing['timestamp'] = pd.to_datetime(existing['timestamp'])
            new_ts = pd.to_datetime(new_row['timestamp'].iloc[0])
            if new_ts in existing['timestamp'].values:
                print("⏩ Bar already exists. Skipping.")
                logging.info(f"Duplicate bar skipped for {filename}")
                return False
            else:
                new_row.to_csv(filename, mode='a', index=False, header=False)
                print(f"✅ Appended new bar to {filename}")
                logging.info(f"New bar appended to {filename}")
                return True
        else:
            print("⚠️ Existing file missing timestamp column. Rewriting...")
            new_row.to_csv(filename, index=False)
            return True
    else:
        new_row.to_csv(filename, index=False)
        print(f"✅ Created new file and saved bar to {filename}")
        logging.info(f"New file created: {filename}")
        return True

def run_volume_analysis():
    try:
        result = subprocess.run(["python", "run_volume_analysis.py"], check=True)
        logging.info("📊 Volume analysis script executed.")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Error running volume analysis: {e}")

# Infinite fetch loop
try:
    while True:
        for ticker in tickers:
            latest_bar = fetch_latest_bar(ticker)
            if latest_bar is not None and not latest_bar.empty:
                filename = f"{ticker.replace('=','_')}_data.csv"
                updated = append_if_new(filename, latest_bar)

                if updated:
                    run_volume_analysis()

        print(f"⏳ Sleeping {delay_seconds} seconds...\n")
        time.sleep(delay_seconds)

except KeyboardInterrupt:
    print("🛑 Stopped live fetching.")
    logging.info("Live fetching stopped manually.")