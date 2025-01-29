import datetime
import requests
import pandas as pd
import numpy as np
import random
import streamlit as st
import time
import json  # Import the json module
from pushbullet import Pushbullet  # Import Pushbullet library

# --- **SECURITY WARNING: HARDCODING API KEY IS INSECURE!** ---
# **DO NOT USE THIS IN PRODUCTION OR SHARE THIS CODE PUBLICLY!**
# **THIS IS ONLY FOR QUICK, LOCAL, PRIVATE TESTING.**
# **IMMEDIATELY REPLACE THIS WITH STREAMLIT SECRETS OR ENVIRONMENT VARIABLES AFTER TESTING.**
PUSHBULLET_API_KEY = "Insert here!!!!!"  # 👈👈👈 **REPLACE THIS WITH YOUR ACTUAL PUSHBULLET ACCESS TOKEN!**


# --- Configuration ---
DEFAULT_PRICE_THRESHOLD = 20000
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
NOTIFICATION_INTERVAL_SECONDS = 60 * 30
PROBABILITY_THRESHOLD_PERCENTILE = 75


# --- Date Range for Historical Data ---
today = datetime.datetime.now()
two_year_ago = today - datetime.timedelta(days=365 * 2)
yesterday_str = today.strftime('%Y-%m-%d')
two_year_ago_str = two_year_ago.strftime('%Y-%m-%d')

# --- Functions ---
def get_current_bitcoin_price():
    """Fetches current Bitcoin price from CoinGecko API."""
    try:
        response = requests.get(COINGECKO_API_URL)
        print(f"CoinGecko API response: {response.text}")  # Debug: Print API response
        response.raise_for_status()
        data = response.json()
        if 'bitcoin' in data and 'usd' in data['bitcoin']:
            return data['bitcoin']['usd']
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching current price from CoinGecko API: {e}")
        return None
    except json.JSONDecodeError:
        st.error("Error: Could not decode JSON from CoinGecko API response.")
        return None

def get_btc_history(symbol='bitcoin', start=two_year_ago_str, end=yesterday_str):
    """Fetches Bitcoin historical data from history.btc123.fans API."""
    url = f'https://history.btc123.fans/api.php?symbol={symbol}&start={start}&end={end}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data and 'data' in data and data['data']:
            df = pd.DataFrame(data['data'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume','other'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['price'] = df['close'].astype(float)
            return df[['date', 'price']]
        else:
            st.error("Error: No data received from historical API or data format incorrect.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching historical data: {e}")
        return None
    except json.JSONDecodeError:
        st.error("Error: Could not decode JSON from historical API. Check API response.")
        return None

def find_x(prob_df, percentile=PROBABILITY_THRESHOLD_PERCENTILE):
    """Calculates the 'x' threshold from the probability DataFrame."""
    probabilities = prob_df['probability'].sort_values(ascending=False)
    n = len(probabilities)
    x = probabilities.iloc[int(n * (percentile / 100))]
    return x

def send_pushbullet_notification(title, body):
    """Sends a push notification via Pushbullet."""
    if not PUSHBULLET_API_KEY:
        st.error("Pushbullet API Key is not configured.  **Check if you replaced 'YOUR_PUSHBULLET_ACCESS_TOKEN' with your actual token!**")
        return

    try:
        pb = Pushbullet(PUSHBULLET_API_KEY)
        push = pb.push_note(title, body)
        print("Pushbullet notification sent successfully.")
    except Exception as e:
        print(f"Error sending Pushbullet notification: {e}")
        st.error(f"Error sending Pushbullet notification: {e}")

def send_notification(text):
    """Sends a test push notification."""
    from pushbullet import Pushbullet # Import Pushbullet inside the function
    try:
        pb = Pushbullet(PUSHBULLET_API_KEY)
        push = pb.push_note("Bitcoin investment 1/4", f"{text} ")
        st.subheader("sent successfully!")
    except Exception as e:
        print(f"Error sending Test notification: {e}")


# --- Streamlit App ---
st.title("Bitcoin Price Monitor and Probability Analysis")

# --- Real-time Price Monitoring ---
st.subheader("Current Bitcoin Price (USD):")
price_placeholder = st.empty()
notification_placeholder = st.empty()
dynamic_threshold_placeholder = st.empty()

# --- Historical Data and Probability Analysis ---
st.subheader("Historical Probability Analysis & Recommendation")
historical_data_placeholder = st.empty()
recommendation_placeholder = st.empty()
probability_chart_placeholder = st.empty()

dynamic_price_threshold = None

# --- Fetch and Process Historical Data ---
df_history = get_btc_history()

if df_history is not None:
    historical_data_placeholder.success("Historical data fetched successfully.")

    prob = pd.DataFrame(columns=['probability'])
    if len(df_history) >= 15:
        for k in range(1500):
            i = random.randint(15, len(df_history) - 1)
            temp_data = df_history.iloc[i - 14:i]
            price_temp = df_history.iloc[i]['price']
            max_temp = temp_data['price'].max()
            prob.loc[k, 'probability'] = price_temp / max_temp

        x = find_x(prob)
        temp_yesterday_price = df_history.iloc[-15:-1]
        max_yes_temp = temp_yesterday_price['price'].max()
        yesterday_price = df_history.iloc[-1]['price']
        prob_yes = yesterday_price / max_yes_temp

        if prob_yes > x:  # CHANGE
            dynamic_price_threshold = prob_yes * max_yes_temp
            print(f"Dynamic threshold is set to {dynamic_price_threshold=}") # Debug: Print dynamic_price_threshold
            dynamic_threshold_placeholder.info(f"Dynamic Price Threshold (based on probability): ${dynamic_price_threshold:.2f} (prob_yes < x)")
            # --- Send Pushbullet Notification for BUY recommendation ---
            subject = "Bitcoin Buy Recommendation!"
            body = f"Based on probability analysis, it's a good time to consider buying Bitcoin. Current probability (prob_yes: {prob_yes:.4f}) is greater than the threshold (x: {x:.4f})."
            send_pushbullet_notification(subject, body)
        else:
            dynamic_price_threshold = None
            dynamic_threshold_placeholder.empty()

        probability_chart_placeholder.subheader("Probability Distribution")
        st.bar_chart(prob['probability'].value_counts(bins=50))

        if prob_yes > x: #  CHANGE
            text_response = f"Recommendation: Consider buying Bitcoin today. (prob_yes: {prob_yes:.4f} < x: {x:.4f}) at {time.time()}) and price of bitcoin {get_current_bitcoin_price()}  UTC"
            recommendation_placeholder.success(text_response)
            send_notification(text_response)
        else:
            recommendation_placeholder.warning(f"Recommendation: Better not to buy Bitcoin today. (prob_yes: {prob_yes:.4f} >= x: {x:.4f})")
    else:
        historical_data_placeholder.error("Not enough historical data to perform probability analysis.")
        dynamic_threshold_placeholder.empty()


# --- Real-time Price Monitoring Loop ---
send_notification("Testing.") # Call test notification function at the start

while True:
    current_price = get_current_bitcoin_price()

    if current_price is not None:
        price_placeholder.metric(label="BTC Price", value=f"${current_price:,.2f}")

        effective_threshold = dynamic_price_threshold
        print(f"{current_price=}") # Debug: Print current_price
        print(f"{effective_threshold=}") # Debug: Print effective_threshold

        if effective_threshold is not None and current_price < effective_threshold:
            notification_placeholder.success(f"🚨 Bitcoin price is below threshold! Current price: ${current_price:,.2f}, Threshold: ${effective_threshold:.2f}")
            subject = "Bitcoin Price Alert!"
            body = f"Giá Bitcoin hiện tại là ${current_price:,.2f}, thấp hơn ngưỡng động ${effective_threshold:.2f}."
            send_pushbullet_notification(subject, body)
        else:
            notification_placeholder.empty()

    time.sleep(NOTIFICATION_INTERVAL_SECONDS)

# --- **SECURITY WARNING: HARDCODING API KEY IS INSECURE!** ---
# **PLEASE READ SECURITY WARNINGS IN PREVIOUS RESPONSES!**