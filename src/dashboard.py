import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
from read_write_postgres import read_from_db
from constants import (
    POSTGRES_TABLE_COIN_DATA,
    COINMARKETCAP_SYMBOLS,
    EXCHANGE_RATES_BASE,
    EXCHANGE_RATE_SYMBOLS,
    )
options_currency = [EXCHANGE_RATES_BASE] + EXCHANGE_RATE_SYMBOLS.split(',') 
options_crypto = COINMARKETCAP_SYMBOLS.split(',')

# Auto-refresh every 20 seconds
count = st_autorefresh(interval=20 * 1000, limit=100, key="data_refresh")

def get_price_data(crypto, fiat):
    query_price = f""" 
    ALTER TABLE crypto_data 
    ALTER COLUMN exchange_rates 
    SET DATA TYPE JSONB 
    USING exchange_rates::JSONB;
    SELECT DISTINCT ON (last_updated) last_updated, price AS {options_currency[0]}_price, 
                                                    exchange_rates->>'{fiat}' AS {fiat}_rate 
    FROM {POSTGRES_TABLE_COIN_DATA} 
    WHERE symbol ='{crypto}'
    ORDER BY last_updated, price ; """

    df_crypto = read_from_db(query_price)
    print(df_crypto)

    if fiat in EXCHANGE_RATE_SYMBOLS.split(','):
        conversion_result = df_crypto[f"{EXCHANGE_RATES_BASE.lower()}_price"] * df_crypto[f"{fiat.lower()}_rate"].astype(float)
    else:
        conversion_result = df_crypto[f"{EXCHANGE_RATES_BASE.lower()}_price"]
    
    return df_crypto, conversion_result


def layout():
       
    #Streamlit 
    #st.set_page_config(page_title="Crypto Dashboard", layout="wide")
    st.title("📈 Live Cryptocurrency Dashboard")
    col1, col2 = st.columns(2)

    with col1:  
        selected_crypto = st.selectbox(label="Select crypto currency:",options=options_crypto)
    with col2:
        selected_currency = st.selectbox(label="Select fiat currency:",options=options_currency)
        
    st.markdown(f"## {selected_crypto}: Latest price in {selected_currency} ")
    
    # Get price data
    df_crypto, conversion_result = get_price_data(selected_crypto, selected_currency)
    # Price Chart
    st.subheader("Price Trend")
    fig = px.line(df_crypto, x='last_updated', y=conversion_result)
   
    st.plotly_chart(fig, use_container_width=True)
        
    st.markdown("## Bitcoin latest price in USD")


if __name__ == "__main__":
    layout()

