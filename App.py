import datetime
import requests
import pandas as pd
import numpy as np
import random
import streamlit as st

# Set date range for Bitcoin historical data
today = datetime.datetime.now()
two_year_ago = today - datetime.timedelta(days=365 * 2)
yesterday_str = today.strftime('%Y-%m-%d')
two_year_ago_str = two_year_ago.strftime('%Y-%m-%d')

# Function to fetch Bitcoin historical data from API
def get_btc_history(symbol='bitcoin', start=two_year_ago_str, end=yesterday_str):
    url = f'https://history.btc123.fans/api.php?symbol={symbol}&start={start}&end={end}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        df = pd.DataFrame(data['data'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume','other'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['price'] = df['close']
        return df[['date', 'price']]
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None

# Fetch data and process
df = get_btc_history()
if df is not None:
    # Display Bitcoin price data as a chart
    st.title("Bitcoin Price Data and Analysis")
    st.subheader("Bitcoin Price Over Time")
    st.line_chart(df.set_index('date')['price'])

    # Calculate probability dataframe
    prob = pd.DataFrame(columns=['probability'])
    for k in range(1500):
        i = random.randint(15, len(df) - 1)
        temp_data = df.iloc[i - 14:i]
        price_temp = df.iloc[i]['price']
        max_temp = temp_data['price'].max()
        prob.loc[k, 'probability'] = price_temp / max_temp

    # Function to calculate 'x' threshold
    def find_x(prob):
        probabilities = prob['probability'].sort_values(ascending=False)
        n = len(probabilities)
        x = probabilities.iloc[int(n * 0.75)]  
        return x

    # Calculate 'x' and 'prob_yes'
    x = find_x(prob)
    temp_yesterday_price = df.iloc[-15:-1]
    max_yes_temp = temp_yesterday_price['price'].max()
    yesterday_price = df.iloc[-1]['price']
    prob_yes = yesterday_price / max_yes_temp

    # Display probability table, x, and prob_yes
    st.subheader("Probability Table")
    st.write(prob)

    st.write(f"Value of x: {x}")
    st.write(f"Value of prob_yes: {prob_yes}")

    # Provide recommendation based on 'x' and 'prob_yes'
    if prob_yes < x:
        st.success("Recommendation: You should consider buying Bitcoin today.")
    else:
        st.warning("Recommendation: It's better not to buy Bitcoin today.")
